"""Module provides datatypes used in the program"""

from abc import abstractmethod
from curses import window
from datetime import datetime, timedelta
import dbm
import logging
from pathlib import Path
import shelve
import time
import enum
from typing import List

import prompt_toolkit
from flufl.lock import Lock

from calcure.classes.task import RootTask, Task
from calcure.classes.timer import Timer
from calcure.classes.workspace import Workspace
from calcure.consts import Importance, Status
from calcure.dialogues import move_cursor_to_x_y
from calcure.singletons import error, global_config


class Shelveable:
    def __init__(self, shelve_filename: Path|str, lock_filename: Path|str) -> None:
        """
        Shelf file constants
        """
        self._shelve_filename = shelve_filename
        self._shelve_file: shelve.Shelf | None = self._initialize_shelve()

        """
        File locking
        """
        lock_acquire_timeout = timedelta(seconds=global_config.LOCK_ACQUIRE_TIMEOUT) # Maximum timeout to wait for lock
        lock_lifetime = timedelta(seconds=global_config.LOCK_LIFETIME)  # Maximum time to write the file will be 10 minutes
        self.tasks_lock = Lock(str(lock_filename), lifetime=lock_lifetime, default_timeout=lock_acquire_timeout)

        """
        Shelf file saving variables
        """
        self._last_save_time = None
        self.changed = False

    def _initialize_shelve(self):
        try:
            shelf: shelve.Shelf = shelve.open(self._shelve_filename, writeback=True, protocol=4)
        except dbm.error as e:
            display_error = ""
            if hasattr(e, "strerror") and isinstance(e.strerror, str):
                display_error += e.strerror + ": "
            if hasattr(e, "filename") and isinstance(e.filename, str):
                display_error += e.filename + " "

            logging.error(display_error)
            raise

        self.hook_initialize_shelf(shelf)

        return shelf
    
    @abstractmethod
    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        raise NotImplementedError()

    def _write_to_shelve_file(self):
        assert self._shelve_file is not None

        logging.info("Saving file...")
        with self.tasks_lock:
            self._shelve_file.close()  # calls sync inside of it 
            self._shelve_file = None # Invalidate shelve file
        
        error.clear_indication = True

    def _save_changes_and_reopen_shelve(self):
        self._write_to_shelve_file()

        # Re-initialize shelve file
        self._shelve_file = self._initialize_shelve()

    def save_if_needed(self):
        if not self.changed:
            return 
    
        if self._last_save_time is None:
            self._save_changes_and_reopen_shelve()
            self._last_save_time = time.time()
            self.changed = False
        
        time_passed = time.time() - self._last_save_time
        if time_passed >= global_config.JOURNAL_SAVE_INTERVAL:
            self._save_changes_and_reopen_shelve()
            self._last_save_time = time.time()
            self.changed = False

class Tasks(Shelveable):
    """List of tasks created by the user"""

    def __init__(self, filename: Path|str, lock_filename: Path|str):
        super().__init__(filename, lock_filename)

    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        if "task_tree" not in shelf:
            shelf["task_tree"] = []
        
        self.task_tree: List[Task] = shelf["task_tree"]
        self.root_task = RootTask(self.task_tree)
    
    @classmethod
    def from_workspace(cls, workspace: Workspace):
        return cls(workspace.workspace_path, workspace.workspace_lock)

    def cleanup(self):
        self._write_to_shelve_file()

    def restore_item_from_archive_with_children(self, task: Task, restore_children: bool):
        task.archive_date = None

        if restore_children:
            children = self.flatten_children_ordered(task, hide_collapsed=True, hide_archived=False)
            for child_task in children:
                if child_task.is_archived:
                    child_task.archive_date = None

    def delete_all_items(self):
        self.task_tree.clear()
        self.changed = True

    @property
    def all_ordered_tasks(self):
        return self.flatten_children_ordered(self.root_task, hide_collapsed=False, hide_archived=False)

    @property
    def viewed_ordered_tasks(self):
        return self.flatten_children_ordered(self.root_task, hide_collapsed=True, hide_archived=True)
    
    @property
    def viewed_archived_ordered_tasks(self):
        archived_tasks = self.flatten_children_ordered(self.root_task, hide_collapsed=False, hide_archived=False)
        return [task for task in archived_tasks if task.is_archived]
    
    def is_valid_number(self, number: int):
        """Check if input is valid and corresponds to an item"""
        return 0 <= number < len(self.viewed_ordered_tasks)

    def is_valid_archive_number(self, number: int):
        """Check if input is valid and corresponds to an item"""
        return 0 <= number < len(self.viewed_archived_ordered_tasks)

    def change_item_importance(self, task: Task, new_importance: Importance):
        """Change task importance"""
        task.importance = new_importance
        self.changed = True

    def change_item_status(self, task: Task, new_status):
        """Change task status"""
        task.status = new_status
        self.changed = True

    def toggle_task_collapse(self, task: Task):
        """Toggle the collapse for the task"""
        task.collapse = not task.collapse
        self.changed = True

    def toggle_item_privacy(self, task):
        """Toggle the privacy for the item with provided id"""
        task.privacy = not task.privacy
        self.changed = True

    def _archive_task(self, task: Task):
        task.archive_date = datetime.now()
        self.changed = True

    def _unarchive_task(self, task: Task):
        task.archive_date = None
        self.changed = True

    def archive_task(self, task_id: int, archive_children: bool):
        task_to_archive = self.get_task_by_id(task_id)
        assert isinstance(task_to_archive, Task), "Cannot archive root task"

        if archive_children:
            tasks_to_archive = self.flatten_children_ordered(task_to_archive, hide_collapsed=False, hide_archived=False)
        else:
            tasks_to_archive = []

        tasks_to_archive.append(task_to_archive)
        for task in tasks_to_archive:
            self._archive_task(task)
        
        self.changed = True

    def delete_task(self, task_id, delete_children):
        assert task_id != 0, "Cannot delete root task"

        task_to_remove = self.get_task_by_id(task_id)
        assert isinstance(task_to_remove, Task), "Cannot delete root task"

        self._delete_task_from_parents(task_to_remove, strict=True)        

        for child_task in task_to_remove.children:
            if not delete_children:
                self.update_parent(child_task, task_to_remove.parent_id, delete_from_parent=False)
            elif delete_children:
                # No need to do anything here, because the parent's reference will go with the children
                pass
        
        self.changed = True
    
    def rename_task(self, task: Task, new_name):
        task.name = new_name
        self.changed = True

    def _delete_task_from_parents(self, task: Task, strict: bool = False):
        parent_task = self.get_task_by_id(task.parent_id)
    
        if strict:
            assert task in parent_task.children, "Cannot find task in parent"

        if task in parent_task.children:
            parent_task.children.remove(task)
        self.changed = True

    def get_indent_count(self, task):
        indent = 0
        while task.item_id != 0:
            indent += 1
            task = self.get_task_by_id(task.parent_id)
    
        return indent

    def get_task_by_id(self, task_id):
        if task_id == 0:
            return self.root_task

        for task in self.all_ordered_tasks:
            if task.item_id == task_id:
                return task 
        raise ValueError()

    def update_parent(self, item: Task, new_parent_id: int, delete_from_parent: bool):
        if delete_from_parent:
            self._delete_task_from_parents(item, strict=True)

        item.parent_id = new_parent_id
        parent_task = self.get_task_by_id(item.parent_id)
        parent_task.children.append(item)
        self.changed = True

    def add_item(self, item: Task):
        parent_task = self.get_task_by_id(item.parent_id)
        parent_task.children.append(item)
        self.changed = True

    @property
    def has_active_timer(self):
        for item in self.all_ordered_tasks:
            if item.timer.is_counting:
                return True
        return False

    def add_subtask(self, task_name, parent_task: Task):
        """Add a subtask for certain task in the journal"""
        child_task = Task(self.generate_id(), task_name,  Status.NOT_STARTED, [], False, parent_id=parent_task.item_id)
        self.add_item(child_task)
        self.changed = True

    def edit_and_display_extra_info(self, task: Task, stdscr: window):
        move_cursor_to_x_y(0, 0)
        task.extra_info = prompt_toolkit.prompt(multiline=True, wrap_lines=True, default=task.extra_info, bottom_toolbar="Use MOD+Enter to save the note")
        stdscr.keypad(True)
        self.changed = True

    def add_timestamp_for_task(self, task: Task):
        """Add a timestamp to this task"""
        task.timer.stamps.append(int(time.time()))
        self.changed = True

    def pause_all_other_timers(self, task: Task):
        """Add a timestamp to this task"""
        if task.timer.is_counting:
            task.timer.stamps.append(int(time.time()))
        self.changed = True

    def reset_timer_for_task(self, task: Task):
        """Reset the timer for one of the tasks"""
        task.timer.stamps = []
        self.changed = True

    def change_deadline(self, task: Task, new_year, new_month, new_day):
        """Reset the timer for one of the tasks"""
        task.year = new_year
        task.month = new_month
        task.day = new_day
        self.changed = True

    def flatten_children_ordered(self, parent_task: Task|RootTask, hide_collapsed: bool = False, hide_archived: bool = True):
        """ This returns the task list ordered by which one will be displayed first """
        flattened_list: List[Task] = []
        nodes_to_go_over = parent_task.children.copy()
        while nodes_to_go_over:
            current_node = nodes_to_go_over.pop(0)
            
            if hide_collapsed and current_node.collapse:
                flattened_list.append(current_node)    
                continue

            nodes_to_go_over = current_node.children + nodes_to_go_over
            
            if hide_archived and current_node.is_archived:
                continue 

            flattened_list.append(current_node)

        return flattened_list

    def get_all_subtasks_for_task(self, father_task: Task|RootTask, direct_subtask: bool):
        subtasks = []
        if direct_subtask:
            subtasks = father_task.children
        else:
            subtasks = self.flatten_children_ordered(father_task)
        
        return subtasks

    def is_task_child_of_other_task(self, parent_task: Task|RootTask, possible_child_task: Task, direct_subtask):
        subtasks = self.get_all_subtasks_for_task(parent_task, direct_subtask)

        return possible_child_task in subtasks

    def swap_task(self, src_task: Task, dst_task: Task):
        if src_task == dst_task:
            logging.error("Cannot move the task to itself")
            return
    
        if self.is_task_child_of_other_task(dst_task, src_task, direct_subtask=False) \
                or self.is_task_child_of_other_task(src_task, dst_task, direct_subtask=False):
            logging.error("Cannot swap child with parent")
            return

        # Get parents for both tasks
        src_task_parent = self.get_task_by_id(src_task.parent_id)
        dst_task_parent = self.get_task_by_id(dst_task.parent_id)

        src_task_index_in_parent = src_task_parent.children.index(src_task)
        dst_task_index_in_parent = dst_task_parent.children.index(dst_task)
        
        src_task_parent.children[src_task_index_in_parent] = dst_task
        dst_task_parent.children[dst_task_index_in_parent] = src_task

        src_task.parent_id = dst_task_parent.item_id
        dst_task.parent_id = src_task_parent.item_id

        self.changed = True

    def move_task(self, src_task: Task, dest_task: Task|RootTask):
        """Move task from certain place to another in the list"""

        if src_task == dest_task:
            logging.error("Cannot move the task to itself")
            return
    
        if self.is_task_child_of_other_task(dest_task, src_task, direct_subtask=True):
            logging.error("Cannot move direct subtask to its parent")
            return

        if isinstance(dest_task, Task) and self.is_task_child_of_other_task(src_task, dest_task, direct_subtask=False):
            logging.error("Cannot move parent to its child")
            return
    
        self.update_parent(src_task, dest_task.item_id, delete_from_parent=True)

        self.changed = True
        

    def is_empty(self):
        return len(self.all_ordered_tasks) == 0

    def generate_id(self):
        """Generate a id for a new item. The id is generated as maximum of existing ids plus one"""
        if self.is_empty():
            return 1
        return max([item.item_id for item in self.all_ordered_tasks]) + 1


class Workspaces(Shelveable):
    def __init__(self, filename: Path):
        super().__init__(filename, global_config.WORKSPACES_LOCK_FILE)
        self.workspace_loaded: Workspace|None = None

    def cleanup(self):
        self._write_to_shelve_file()

    def is_valid_number(self, number: int):
        return 0 <= number < len(self.workspaces)

    def delete_workspace(self, workspace: Workspace):
        if workspace in self.workspaces:
            self.workspaces.remove(workspace)
        
        if self.workspace_loaded == workspace:
            self.workspace_loaded = None

    def add_workspace(self, workspace: Workspace):
        self.workspaces.append(workspace)

    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        if "workspaces" not in shelf:
            shelf["workspaces"] = []

        self.workspaces: List[Workspace] = shelf["workspaces"]
        
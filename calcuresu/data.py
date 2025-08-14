"""Module provides datatypes used in the program"""

from abc import abstractmethod
from contextlib import contextmanager
from curses import window
import curses
from datetime import date, datetime, timedelta
import dbm
import dbm.sqlite3
import logging
import os
from pathlib import Path
import re
import shelve
import time
import enum
from typing import Any, List

import prompt_toolkit
from flufl.lock import AlreadyLockedError, Lock, LockState, TimeOutError

from calcuresu.classes.task import RootTask, Task, TaskFilter
from calcuresu.classes.timer import Timer
from calcuresu.classes.workspace import Workspace
from calcuresu.consts import Filters, Importance, Status
from calcuresu.dialogues import ask_confirmation, move_cursor_to_x_y
from calcuresu.screen import Screen
from calcuresu.singletons import error, global_config


class Shelveable:
    def __init__(self, shelve_filename: Path|str, lock_filename: Path|str) -> None:
        """
        Shelf file constants
        """
        self._shelve_filename = shelve_filename
        self._shelve_file: shelve.Shelf | None = None

        """
        File locking
        """
        lock_acquire_timeout = timedelta(seconds=global_config.LOCK_ACQUIRE_TIMEOUT.value) # Maximum timeout to wait for lock
        lock_lifetime = timedelta(seconds=global_config.LOCK_LIFETIME.value)  # Maximum time to write the file
        self.tasks_lock = Lock(str(lock_filename), lifetime=lock_lifetime, default_timeout=lock_acquire_timeout)

        """
        Shelf file saving variables
        """
        self.changed = False

        """ Last file modification time """
        self.last_shelve_modification_time = None 

    def initialize(self, stdscr: curses.window, screen: Screen):
        shelve = self.reopen_shelve_locked(stdscr, screen)
        
        self.last_shelve_modification_time = self._get_shelve_last_modification_time()
        return shelve

    def _initialize_shelve(self):
        try:
            shelf: shelve.Shelf = shelve.open(self._shelve_filename, writeback=True, protocol=4)
        except dbm.error as e:
            display_error = ""
            if hasattr(e, "strerror") and isinstance(e.strerror, str): # noqa
                display_error += e.strerror + ": "
            if hasattr(e, "filename") and isinstance(e.filename, str): #
                display_error += e.filename + " "

            logging.error(display_error)
            raise

        self.hook_initialize_shelf(shelf)

        return shelf

    def cleanup(self):
        self.tasks_lock.unlock(unconditionally=True)

    @abstractmethod
    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        raise NotImplementedError()

    def _write_to_shelve_file_nolock(self):
        assert self._shelve_file is not None

        logging.info("Saving file...")
        self._shelve_file.close()  # calls sync inside of it 
        self._shelve_file = None # Invalidate shelve file
        error.clear_indication = True

    def _write_to_shelve_file_locked(self):
        with self.tasks_lock:
            self._write_to_shelve_file_nolock()

    def reopen_shelve_nolock(self):
        # Re-initialize shelve file
        self._shelve_file = self._initialize_shelve()
        self.last_shelve_modification_time = self._get_shelve_last_modification_time()

    def reopen_shelve_locked(self,stdscr: curses.window, screen: Screen):
        with try_to_lock_auto_unlock(stdscr, screen, self) as locked:
            if locked:
                self.reopen_shelve_nolock()

            return locked

    def reopen_shelve_if_needed_locked(self,stdscr: curses.window, screen: Screen):
        if self.has_shelve_file_changed():
            try:
                if self.reopen_shelve_locked(stdscr, screen):
                    screen.next_need_refresh = True
                    return True
            except dbm.sqlite3.error:
                # The other end didn't finish writing probably
                return True
        return False


    def _save_changes_and_reopen_shelve_nolock(self):
        self._write_to_shelve_file_nolock()
        self.reopen_shelve_nolock()
    
    def _get_shelve_last_modification_time(self):
        return int(os.stat(self._shelve_filename).st_mtime)

    def has_shelve_file_changed(self):
        # Note: we don't want to only trust the last modification time, due to computers having different clocks
        current_modification_time = self._get_shelve_last_modification_time()
        
        if current_modification_time < self.last_shelve_modification_time:
            raise RuntimeError("One of the computers editing this file has a different time than yours! Find them and handle it...")

        return current_modification_time > self.last_shelve_modification_time

    def is_other_user_editing(self):
        # "LockState.theirs" is basically for other processes on the same computer
        lockfile_state = self.tasks_lock.state
        if lockfile_state in [LockState.unlocked, LockState.ours, LockState.ours_expired]:
            return False 
        
        hostname, pid, _ = self.tasks_lock.details
        lockfile_expiration = self.tasks_lock.expiration

        if hostname == self.tasks_lock.hostname:
            logging.warning(f"Another process on your pc ({pid}) has taken the lock. It expires in {lockfile_expiration}")
            return True
        
        return lockfile_expiration < datetime.now() # Lock has expired and we can use it now
        
    @property
    def our_lock(self):
        return self.tasks_lock.state == LockState.ours

    def force_acquire_lock(self):
        try:
            self.tasks_lock.lock(timeout=1)
        except TimeOutError:
            self.tasks_lock._break()
            self.tasks_lock.lock()  # Use default timeout

    def try_lock_default_timeout(self):
        try:
            self.lock(timeout=None)
            return True
        except TimeOutError:
            return False 

    def lock(self, timeout: int|None):
        return self.tasks_lock.lock(timeout)

    def unlock(self):
        return self.tasks_lock.unlock(unconditionally=True)

    def refresh_lock(self):
        assert self.our_lock
        self.tasks_lock.refresh(unconditionally=True)

    def save_if_needed_nolock(self):
        if not self.changed:
            return 

        self._save_changes_and_reopen_shelve_nolock()
        self.changed = False

    def save_if_needed_locked(self):
        if not self.changed:
            return 

        with self.tasks_lock:
            self.save_if_needed_nolock()    


@contextmanager
def try_to_lock_auto_unlock(stdscr: curses.window, screen: Screen, shelvable: Shelveable):
    locked = try_to_lock(stdscr, screen, shelvable)
        
    try:
        yield locked
    
    finally:
        if locked:
            shelvable.unlock()

def try_to_lock(stdscr: curses.window, screen: Screen, shelvable: Shelveable):

    if shelvable.our_lock:
        shelvable.refresh_lock()
        return True 

    if shelvable.try_lock_default_timeout():
        return True
    if ask_confirmation(stdscr, screen, "Another user is currently editing. Are you sure you want to forcefully take the lock? (their lock has a timeout)"):
        shelvable.force_acquire_lock()
        return True
    
    return False 


class Tasks(Shelveable):
    """List of tasks created by the user"""

    def __init__(self, filename: Path|str, lock_filename: Path|str):
        super().__init__(filename, lock_filename)
        self._user_display_filter: TaskFilter|None = None

    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        if "task_tree" not in shelf:
            shelf["task_tree"] = []
        
        self.task_tree: List[Task] = shelf["task_tree"]
        self.root_task = RootTask(self.task_tree)

    @property
    def filter(self):
        return self._user_display_filter

    @filter.setter
    def filter(self, new_filter: TaskFilter):
        self._user_display_filter = new_filter

    def clear_filter(self):
        self._user_display_filter = None

    @property
    def has_filter(self):
        return self._user_display_filter is not None
    
    @classmethod
    def from_workspace(cls, workspace: Workspace):
        return cls(workspace.workspace_path, workspace.workspace_lock)

    def restore_item_from_archive_with_children(self, task: Task, restore_children: bool):
        task.archive_date = None

        if restore_children:
            children = self.flatten_children_ordered(task, hide_collapsed=True, hide_archived=False)
            for child_task in children:
                if child_task.is_archived:
                    child_task.archive_date = None
        self.changed = True

    def delete_all_items(self):
        self.task_tree.clear()
        self.changed = True

    @property
    def all_ordered_tasks(self):
        return self.flatten_children_ordered(self.root_task, hide_collapsed=False, hide_archived=False)

    @property
    def viewed_ordered_tasks(self):
        if self.has_filter:
            # We want to see collapsed children here
            all_tasks = self.flatten_children_ordered(self.root_task, hide_collapsed=False, hide_archived=True)
            return [task for task in all_tasks if self._user_display_filter in task]
        else:
            return self.flatten_children_ordered(self.root_task, hide_collapsed=True, hide_archived=True)
    
    @property
    def viewed_archived_ordered_tasks(self):
        archived_tasks = [task for task in self.all_ordered_tasks if task.is_archived]
        if self.has_filter:
            return [task for task in archived_tasks if self._user_display_filter in task]
        else:
            return archived_tasks
    
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
        task.extra_info = prompt_toolkit.prompt(multiline=True, wrap_lines=True, default=task.extra_info, bottom_toolbar="Use ALTp+Enter to save the note")
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

    def change_deadline(self, task: Task, deadline_date: date|None):
        """Reset the timer for one of the tasks"""
        task.deadline = deadline_date
        self.changed = True

    def flatten_children_ordered(self, parent_task: Task|RootTask, hide_collapsed: bool = False, hide_archived: bool = True):
        """ This returns the task list ordered by which one will be displayed first """
        flattened_list: List[Task] = []
        nodes_to_go_over = parent_task.children.copy()
        while nodes_to_go_over:
            current_node = nodes_to_go_over.pop(0)
            
            if not (hide_collapsed and current_node.collapse):
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
    def __init__(self, filename: Path | str, lockfile: Path | str):
        super().__init__(filename, lockfile)
        self.workspace_loaded: Workspace|None = None

    def is_valid_number(self, number: int):
        return 0 <= number < len(self.workspaces)

    def delete_workspace(self, workspace: Workspace, delete_files: bool):
        if workspace in self.workspaces:
            self.workspaces.remove(workspace)
        
        if self.workspace_loaded == workspace:
            self.workspace_loaded = None

        if delete_files:
            for filepath in [f"{workspace.workspace_path}.db", workspace.workspace_lock]:
                delete_path = Path(filepath)
                try:
                    if delete_path.is_file():
                        delete_path.unlink()
                except Exception as e:
                    logging.error(e)
        
        self.changed = True

    def add_workspace(self, workspace: Workspace):
        self.workspaces.append(workspace)
        self.changed = True

    def hook_initialize_shelf(self, shelf: shelve.Shelf):
        if "workspaces" not in shelf:
            shelf["workspaces"] = []

        self.workspaces: List[Workspace] = shelf["workspaces"]
        
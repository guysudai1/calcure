"""Module provides datatypes used in the program"""

import logging
import time
import enum
from typing import List

from calcure.classes.task import RootTask, Task
from calcure.classes.timer import Timer


class AppState(enum.Enum):
    """Possible focus states of the application"""
    JOURNAL = 1
    HELP = 2
    EXIT = 3
    WELCOME = 4


class Status(enum.Enum):
    """Status of events and tasks"""
    NORMAL = 1
    DONE = 2
    IMPORTANT = 3
    UNIMPORTANT = 4


class Tasks:
    """List of tasks created by the user"""

    def __init__(self):
        self.task_tree: List[Task] = []
        self._root_task = RootTask(self.task_tree)

    def delete_all_items(self):
        self.task_tree.clear()

    def _get_ordered_tasks(self, hide_collapsed: bool):
        task_list = []

        for task in self.task_tree:
            task_list.append(task)
            if not hide_collapsed or not task.collapse:
                task_list.extend(self.flatten_children_ordered(task, hide_collapsed=True))

        return task_list

    @property
    def all_ordered_tasks(self):
        return self._get_ordered_tasks(hide_collapsed=False)

    @property
    def viewed_ordered_tasks(self):
        return self._get_ordered_tasks(hide_collapsed=True)
    
    def is_valid_number(self, number: int):
        """Check if input is valid and corresponds to an item"""
        return 0 <= number < len(self.all_ordered_tasks)

    def toggle_item_status(self, task: Task, new_status):
        """Toggle the status for the item with provided id"""
        if task.status == new_status:
            task.status = Status.NORMAL
        else:
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

    def delete_task(self, task_id, delete_children):
        assert task_id != 0, "Cannot delete root task"

        task_to_remove: Task = self.get_task_by_id(task_id)
        self._delete_task_from_parents(task_to_remove)        

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

    def _delete_task_from_parents(self, task: Task):
        parent_task = self.get_task_by_id(task.parent_id)
        parent_task.children.remove(task)
        self.changed = True

    def get_indent_count(self, task):
        indent = 0
        while task.parent_id != 0:
            indent += 1
            task = self.get_task_by_id(task.parent_id)
    
        return indent

    def get_task_by_id(self, task_id):
        if task_id == 0:
            return self._root_task

        for task in self.all_ordered_tasks:
            if task.item_id == task_id:
                return task 
        raise ValueError()

    def update_parent(self, item: Task, new_parent_id: int, delete_from_parent: bool):
        if delete_from_parent:
            self._delete_task_from_parents(item)

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
        child_task = Task(self.generate_id(), task_name,  Status.NORMAL, Timer([]), False, parent_id=parent_task.item_id)
        self.add_item(child_task)
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

    def flatten_children_ordered(self, parent_task: Task, hide_collapsed: bool = False):
        """ This returns the task list ordered by which one will be displayed first """
        flattened_list = []
        nodes_to_go_over = parent_task.children.copy()
        while nodes_to_go_over:
            current_node = nodes_to_go_over.pop(0)
            flattened_list.append(current_node)
            if not hide_collapsed or not current_node.collapse:
                nodes_to_go_over = current_node.children + nodes_to_go_over

        return flattened_list

    def get_all_subtasks_for_task(self, father_task: Task, direct_subtask: bool):
        subtasks = []
        if direct_subtask:
            subtasks = father_task.children
        else:
            subtasks = self.flatten_children_ordered(father_task)
        
        return subtasks

    def is_task_child_of_other_task(self, parent_task: Task, possible_child_task: Task, direct_subtask):
        subtasks = self.get_all_subtasks_for_task(parent_task, direct_subtask)

        return possible_child_task in subtasks

    def swap_task(self, src_task: Task, dst_task: Task):
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

    def move_task(self, src_task: Task, dest_task: Task):
        """Move task from certain place to another in the list"""

        if src_task == dest_task:
            logging.error("Cannot move the task to itself")
            return
    
        if self.is_task_child_of_other_task(dest_task, src_task, direct_subtask=True):
            logging.error("Cannot move direct subtask to its parent")
            return

        if self.is_task_child_of_other_task(src_task, dest_task, direct_subtask=False):
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


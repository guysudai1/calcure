from typing import List


class Task:
    """Tasks created by the user"""

    def __init__(self, item_id, name, status, timer, privacy, parent_id, collapse=False, year=0, month=0, day=0, calendar_number=None):
        self.item_id = item_id
        self.name = name
        self.status = status
        self.timer = timer
        self.privacy = privacy
        self.year = year
        self.month = month
        self.day = day
        self.calendar_number = calendar_number
        self.parent_id = parent_id
        self.children: List[Task] = []
        self.collapse = collapse

    def __eq__(self, other):
        return self.item_id == other.item_id

class RootTask:
    """
    This is a fake item to use as the root of all other tasks
    """
    def __init__(self, task_tree: List[Task]) -> None:
        self.item_id = 0
        self.name = "FAKE ROOT ITEM"
        self.children = task_tree  # Reference to the task tree

    @property 
    def parent_id(self):
        raise Exception("Root task has no parent id")
    
    def __eq__(self, other):
        return self.item_id == other.item_id

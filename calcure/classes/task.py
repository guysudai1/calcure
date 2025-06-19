from typing import List

from calcure.classes.timer import Timer
from calcure.consts import Importance, Status


class Task:
    """Tasks created by the user"""

    def __init__(self, item_id, name, status, timestamps: List[str], privacy, parent_id, importance=Importance.UNDECIDED, collapse=False, year=0, month=0, day=0):
        """
        Node Management
        """
        self.item_id: int = item_id
        self.parent_id: int = parent_id

        """
        General task properties
        """
        self.name: str = name
        self.status: Status = status
        self.privacy: bool = privacy
        self.collapse: bool = collapse
        self.importance: Importance = importance

        """
        Task Timer
        """
        self.timer: Timer = Timer(timestamps)

        """
        Deadline variables
        """
        self.year: int = year
        self.month: int = month
        self.day: int = day
        self.children: List[Task] = []

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.item_id == other.item_id
        
        raise NotImplementedError()

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

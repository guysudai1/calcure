from datetime import date
import re
from typing import Any, List

from prompt_toolkit import PromptSession
from prompt_toolkit.history import History

from calcure.classes.timer import Timer
from calcure.consts import Filters, Importance, Status

class TaskFilter:
    def __init__(self, filter_type, filter_content) -> None:
        self.filter_type: Filters = filter_type
        self.filter_content: Any = filter_content

    def __str__(self):
        if self.filter_type in [Filters.STATUS, Filters.IMPORTANCE]:
            return f"{self.filter_type.name} == {self.filter_content}"
        elif self.filter_type in [Filters.NAME, Filters.EXTRA_INFO]:
            return f"{self.filter_type.name} regex '{self.filter_content}'"
        
        raise NotImplementedError()


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
        self.extra_info: str = ""

        """
        Task Timer
        """
        self.timer: Timer = Timer(timestamps)

        """
        Deadline variables
        """
        self.deadline: date|None = None
        self.children: List[Task] = []

        """
        Archive variables
        """
        self.archive_date: date|None = None

    @property
    def has_deadline(self):
        return self.deadline is not None

    @property
    def is_archived(self):
        return self.archive_date is not None

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.item_id == other.item_id
        
        raise NotImplementedError()
    
    def __contains__(self, user_filter):
        if isinstance(user_filter, TaskFilter):
            match user_filter.filter_type:
                case Filters.NAME | Filters.EXTRA_INFO:
                    if user_filter.filter_type == Filters.NAME:
                        filter_field = self.name
                    elif user_filter.filter_type == Filters.EXTRA_INFO:
                        filter_field = self.extra_info
                    else:
                        raise Exception("Invalid filter type")
                    
                    return re.match(user_filter.filter_content, filter_field) is not None
                case Filters.STATUS | Filters.IMPORTANCE:
                    if user_filter.filter_type == Filters.STATUS:
                        filter_field = self.status
                    elif user_filter.filter_type == Filters.IMPORTANCE:
                        filter_field = self.importance
                    else:
                        raise Exception("Invalid filter type")
                    
                    return filter_field == user_filter.filter_content
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

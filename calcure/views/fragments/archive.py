from calcure.base_view import View

from calcure.classes.task import RootTask, Task
from calcure.colors import Color
from calcure.configuration import AppState
from calcure.data import Tasks
from calcure.screen import Screen
from calcure.singletons import global_config
from calcure.translations.en import MSG_TS_NOTHING
from calcure.views.fragments.filter import FilterView
from calcure.views.fragments.status import TaskStatusView
from calcure.views.fragments.task import TaskView

class ArchiveView(View):
    """Displays a list of all tasks"""

    def __init__(self, stdscr, y, x, user_tasks: Tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen: Screen = screen

    def render(self):
        """Render the list of tasks"""
        all_tasks = self.user_tasks.viewed_archived_ordered_tasks

        if not all_tasks and global_config.SHOW_NOTHING_PLANNED.value:
            self.display_line(self.y, self.x, MSG_TS_NOTHING, Color.TITLE)
        
        relevant_task_list = all_tasks[self.screen.offset:]

        status_view = TaskStatusView(self.stdscr, self.y, self.x, self.screen, relevant_task_list, all_tasks)
        status_view.render()
        self.y += 1
        
        if self.user_tasks.has_filter:
            assert self.user_tasks.filter is not None, "Shouldnt reach this"
            filter_view = FilterView(self.stdscr, self.y, self.x, self.user_tasks.filter)
            filter_view.render()
            self.y += 1

        for index, task in enumerate(relevant_task_list, start=self.screen.offset):
            if self.y + 1 >= self.screen.y_max:
                break
            
            task_view = TaskView(self.stdscr, self.y, self.x, task, self.screen, 
                                 indent=self.user_tasks.get_indent_count(task), parent=self.user_tasks.get_task_by_id(task.parent_id))
            task_view.render()
            if self.screen.selection_mode:
                self.display_line(self.y, self.x, str(index + 1), Color.ACTIVE_PANE)
            self.y += 1

        self.y += 1

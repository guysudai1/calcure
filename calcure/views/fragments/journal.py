from calcure.base_view import View
from calcure.colors import Color
from calcure.configuration import AppState
from calcure.data import Tasks
from calcure.singletons import global_config
from calcure.translations.en import MSG_TS_NOTHING
from calcure.views.fragments.task import TaskView

class JournalView(View):
    """Displays a list of all tasks"""

    def __init__(self, stdscr, y, x, user_tasks: Tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen


    def render(self):
        """Render the list of tasks"""
        if self.y == 0:
            self.y += 1

        all_tasks = self.user_tasks.viewed_ordered_tasks

        if not all_tasks and global_config.SHOW_NOTHING_PLANNED:
            self.display_line(self.y, self.x, MSG_TS_NOTHING, Color.UNIMPORTANT)
        
        relevant_task_list = all_tasks[self.screen.offset:]
        self.display_line(self.y - 1, self.x, color=Color.TITLE, bold=True,
                          text=f"# Tasks displayed: {len(relevant_task_list)}/{len(all_tasks)}. Offset: {self.screen.offset}")
        for index, task in enumerate(relevant_task_list, start=self.screen.offset):
            task_view = TaskView(self.stdscr, self.y, self.x, task, self.screen, indent=self.user_tasks.get_indent_count(task))
            task_view.render()
            if self.screen.selection_mode and self.screen.state == AppState.JOURNAL:
                self.display_line(self.y, self.x, str(index + 1), Color.ACTIVE_PANE)
            self.y += 1

        self.y += 1
        # for index, task in enumerate(self.user_ics_tasks.items):
        #     task_view = TaskView(self.stdscr, self.y, self.x, task, self.screen)
        #     task_view.render()
        #     self.y += 1

import time
from calcuresu.base_view import View
from calcuresu.configuration import AppState
from calcuresu.data import Tasks
from calcuresu.views.fragments.header import HeaderView
from calcuresu.singletons import global_config
from calcuresu.views.fragments.journal import JournalView


class JournalScreenView(View):
    def __init__(self, stdscr, y, x, user_tasks: Tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen

    def render(self):
        """Journal view showing all tasks"""
        if not self.screen.need_refresh:
            return

        self.screen.currently_drawn = AppState.JOURNAL
        if self.screen.x_max < 6 or self.screen.y_max < 3:
            return

        # Display header and footer:
        journal_header = global_config.JOURNAL_HEADER.value
        journal_title = f"{journal_header} - {self.user_tasks._shelve_filename}"
        header_view = HeaderView(self.stdscr, 0, 0, journal_title, self.screen)
        header_view.render()

        # Display the tasks:
        journal_view = JournalView(self.stdscr, 1, 0, self.user_tasks, self.screen)
        journal_view.render()

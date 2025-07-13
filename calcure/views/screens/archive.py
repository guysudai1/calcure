import time
from calcure.base_view import View
from calcure.configuration import AppState
from calcure.data import Tasks
from calcure.views.fragments.archive import ArchiveView
from calcure.views.fragments.header import HeaderView
from calcure.singletons import global_config
from calcure.views.fragments.journal import JournalView


class ArchiveScreenView(View):
    def __init__(self, stdscr, y, x, user_tasks: Tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen

    def render(self):
        """Journal view showing all tasks"""
        self.user_tasks.save_if_needed()

        self.screen.currently_drawn = AppState.ARCHIVE
        if self.screen.x_max < 6 or self.screen.y_max < 3:
            return

        # Display header and footer:
        archive_header = global_config.ARCHIVE_HEADER.value
        archive_title = f"{archive_header} - {self.user_tasks._shelve_filename}"

        header_view = HeaderView(self.stdscr, 0, 0, archive_title, self.screen)
        header_view.render()

        # Display the tasks:
        journal_view = ArchiveView(self.stdscr, 1, self.screen.x_min, self.user_tasks, self.screen)
        journal_view.render()

from calcure.base_view import View
from calcure.configuration import AppState
from calcure.views.fragments.header import HeaderView
from calcure.singletons import global_config
from calcure.views.fragments.journal import JournalView


class JournalScreenView(View):
    def __init__(self, stdscr, y, x, user_tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen

    def render(self):
        """Journal view showing all tasks"""
        self.screen.currently_drawn = AppState.JOURNAL
        if self.screen.x_max < 6 or self.screen.y_max < 3:
            return

        # Display header and footer:
        header_view = HeaderView(self.stdscr, 0, 0, global_config.JOURNAL_HEADER, self.screen)
        header_view.render()

        # Display the tasks:
        journal_view = JournalView(self.stdscr, 2, self.screen.x_min, self.user_tasks, self.screen)
        journal_view.render()

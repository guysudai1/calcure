import time
from calcuresu.base_view import View
from calcuresu.configuration import AppState
from calcuresu.data import Tasks
from calcuresu.views.fragments.color import ColorView
from calcuresu.views.fragments.header import HeaderView
from calcuresu.singletons import global_config


class ColorScreenView(View):
    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def render(self):
        """Journal view showing all tasks"""
        if not self.screen.need_refresh:
            return

        self.screen.currently_drawn = AppState.JOURNAL
        if self.screen.x_max < 6 or self.screen.y_max < 3:
            return

        # Display header and footer:
        header_view = HeaderView(self.stdscr, 0, 0, "Color View", self.screen)
        header_view.render()

        # Display the tasks:
        color_view = ColorView(self.stdscr, 1, 0, self.screen)
        color_view.render()

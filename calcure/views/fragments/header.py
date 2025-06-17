import time
from calcure.base_view import View
from calcure.colors import Color
from calcure.configuration import AppState
from calcure.views.fragments.title import TitleView
from calcure.singletons import global_config

class HeaderView(View):
    """Show the header that includes the time, and title"""

    def __init__(self, stdscr, y, x, title, screen):
        super().__init__(stdscr, y, x)
        self.title = title
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        _, x_max = self.stdscr.getmaxyx()

        # Show title:
        title_view = TitleView(self.stdscr, 0, self.screen.x_min, self.title, self.screen)
        title_view.render()

        if self.screen.currently_drawn == AppState.JOURNAL and self.screen.split:
            return

        # Show time:
        time_string = time.strftime("%H:%M", time.localtime())
        size_allows = len(time_string) < self.screen.x_max - len(self.title)
        if global_config.SHOW_CURRENT_TIME and size_allows:
            self.display_line(0, (self.screen.x_max // 2 - 2), time_string, Color.TIME)

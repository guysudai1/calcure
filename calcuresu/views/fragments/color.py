import curses
import time
from calcuresu.base_view import View
from calcuresu.colors import Color, initialize_colors
from calcuresu.configuration import AppState
from calcuresu.views.fragments.title import TitleView
from calcuresu.singletons import global_config

class ColorView(View):
    """Show the header that includes the time, and title"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    @staticmethod
    def revert_to_original_colors():
        initialize_colors(global_config)

    @staticmethod
    def initialize_all_colors():
        for i in range(256):
            curses.init_pair(i, i, 0)

    def render(self):
        """Render this view on the screen"""
        y_max, x_max = self.stdscr.getmaxyx()
        x = 1
        y = 1

        self.initialize_all_colors()
        
        for i in range(256):
            self.stdscr.addstr(y, x, f'{i}', curses.color_pair(i))
            x += 5
            if x >= (x_max - 1):
                x = 1
                y += 1
        
        self.revert_to_original_colors()

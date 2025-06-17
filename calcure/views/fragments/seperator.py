from calcure.base_view import View
from calcure.colors import Color
from calcure.singletons import global_config

class SeparatorView(View):
    """Display the separator in the split screen"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        _, x_max = self.stdscr.getmaxyx()
        x_separator = x_max - self.screen.journal_pane_width
        y_cell = (self.screen.y_max - 3) // 6
        height = self.screen.number_of_weeks * y_cell + 2
        for row in range(height):
            self.display_line(row, x_separator, global_config.SEPARATOR_ICON, Color.SEPARATOR)

from calcure.base_view import View
from calcure.colors import Color
from calcure.singletons import global_config

class TitleView(View):
    """Show the title in the header"""

    def __init__(self, stdscr, y, x, title, screen):
        super().__init__(stdscr, y, x)
        self.title = title
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        self.display_line(0, self.screen.x_min, self.title, Color.HEADER, global_config.BOLD_TITLE, global_config.UNDERLINED_TITLE)

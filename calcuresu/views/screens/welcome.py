from calcuresu.base_view import View
from calcuresu.colors import Color
from calcuresu.consts import VERSION
from calcuresu.translations.en import WELCOME_MESSAGES
from calcuresu.singletons import global_config

class WelcomeScreenView(View):
    """Welcome screen displaying greeting info on the first run"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def calibrate_position(self):
        """Depending on the screen space calculate the best position"""
        self.y_max, self.x_max = self.stdscr.getmaxyx()

    def render(self):
        """Draw the welcome screen"""

        if not self.screen.need_refresh:
            return

        self.calibrate_position()
        self.stdscr.clear()
        self.fill_background()

        d_x = self.x_max//2
        d_y = self.y_max//2 - 5

        for message, color in WELCOME_MESSAGES:
            if message is not None:
                self.display_line(d_y, d_x - len(message) // 2, message, color)
            d_y += 1

from calcuresu.base_view import View
from calcuresu.colors import Color
from calcuresu.consts import VERSION
from calcuresu.translations.en import MSG_SITE, MSG_WELCOME_1, MSG_WELCOME_2, MSG_WELCOME_3, MSG_WELCOME_4, MSG_WELCOME_5
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
        self.calibrate_position()
        self.stdscr.clear()
        self.fill_background()

        if self.x_max < len(MSG_WELCOME_4)+2 or self.y_max < 12:
            self.display_line(0, 0, "Welcome!", Color.ACTIVE_PANE)
            return

        d_x = self.x_max//2
        d_y = self.y_max//2 - 5

        self.display_line(d_y, d_x - len(MSG_WELCOME_1+VERSION+" ")//2, f"{MSG_WELCOME_1} {VERSION}", Color.ACTIVE_PANE)
        self.display_line(d_y + 1, d_x - len(MSG_WELCOME_2)//2, MSG_WELCOME_2, Color.HINTS)
        self.display_line(d_y + 6, d_x - len(MSG_WELCOME_4)//2, MSG_WELCOME_4, Color.HINTS)
        self.display_line(d_y + 7, d_x - len(MSG_SITE)//2, MSG_SITE, Color.TITLE)
        self.display_line(d_y + 9, d_x - len(MSG_WELCOME_5)//2, MSG_WELCOME_5, Color.HINTS)
        

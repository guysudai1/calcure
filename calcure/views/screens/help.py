from calcure.base_view import View
from calcure.colors import Color
from calcure.consts import VERSION
from calcure.translations.en import KEYS_CALENDAR, KEYS_GENERAL, KEYS_TODO, MSG_INFO, MSG_NAME, MSG_SITE, MSG_VIM, TITLE_KEYS_CALENDAR, TITLE_KEYS_GENERAL, TITLE_KEYS_JOURNAL
from calcure.singletons import global_config

class HelpScreenView(View):
    """Help screen displaying information about keybindings"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def calibrate_position(self):
        """Depending on the screen space calculate the best position"""
        self.y_max, self.x_max = self.stdscr.getmaxyx()

        if self.x_max < 102:
            self.global_shift_x = 0
            self.shift_x = 0
            self.shift_y = 6 + len(KEYS_GENERAL) + len(KEYS_CALENDAR)
        else:
            self.global_shift_x = (self.x_max - 102) // 2
            self.shift_x = 45
            self.shift_y = 2

        if self.y_max > 20 and self.x_max >= 102:
            self.global_shift_y = (self.y_max - 25) // 2
        else:
            self.global_shift_y = 0

    def render(self):
        """Draw the help screen"""
        self.calibrate_position()
        if self.x_max < 6 or self.y_max < 3:
            return
        self.stdscr.clear()
        self.fill_background()

        # Left column:
        self.display_line(self.global_shift_y, self.global_shift_x + 1, f"{MSG_NAME} {VERSION}",
                            Color.ACTIVE_PANE, global_config.BOLD_TITLE, global_config.UNDERLINED_TITLE)
        self.display_line(self.global_shift_y + 2, self.global_shift_x + 8,
                          TITLE_KEYS_GENERAL, Color.TITLE, global_config.BOLD_TITLE, global_config.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_GENERAL):
            self.display_line(self.global_shift_y + index + 3, self.global_shift_x, key, Color.ACTIVE_PANE)
            self.display_line(self.global_shift_y + index + 3, self.global_shift_x + 8, KEYS_GENERAL[key], Color.TODO)

        self.display_line(self.global_shift_y + 4 + len(KEYS_GENERAL), self.global_shift_x + 8,
                          TITLE_KEYS_CALENDAR, Color.TITLE, global_config.BOLD_TITLE, global_config.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_CALENDAR):
            self.display_line(self.global_shift_y + index + 5 + len(KEYS_GENERAL), self.global_shift_x, key, Color.ACTIVE_PANE)
            self.display_line(self.global_shift_y + index + 5 + len(KEYS_GENERAL), self.global_shift_x + 8,
                                                                            KEYS_CALENDAR[key], Color.TODO)

        # Right column:
        d_x = self.global_shift_x + self.shift_x
        d_y = self.global_shift_y + self.shift_y
        self.display_line(d_y, d_x + 8, TITLE_KEYS_JOURNAL, Color.TITLE, global_config.BOLD_TITLE, global_config.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_TODO):
            self.display_line(d_y + index + 1, d_x, key, Color.ACTIVE_PANE)
            self.display_line(d_y + index + 1, d_x + 8, KEYS_TODO[key], Color.TODO)

        # Additional info:
        d_x = self.global_shift_x + self.shift_x + 8
        d_y = self.global_shift_y + len(KEYS_TODO) + self.shift_y
        self.display_line(d_y + 2, d_x, MSG_VIM, Color.ACTIVE_PANE)
        self.display_line(d_y + 4, d_x, MSG_INFO, Color.TODO)
        self.display_line(d_y + 5, d_x, MSG_SITE, Color.TITLE)

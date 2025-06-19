import time
from calcure.base_view import View
from calcure.colors import Color
from calcure.dialogues import clear_line
from calcure.singletons import error
from calcure.translations.en import MSG_ERRORS, MSG_INPUT

class ErrorView(View):
    """Display the error messages"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen
        self.error = error

    def render(self):
        """Render this view on the screen"""
        if self.error.clear_indication:
            clear_line(self.stdscr, self.screen.y_max - 2)
            self.error.clear_indication = False

        if self.error.has_occurred:
            clear_line(self.stdscr, self.screen.y_max - 2)

            # Depending on error type, display different messages:
            if self.error.number_of_errors >= 1:
                if self.error.number_of_errors == 1:
                    self.display_line(self.screen.y_max - 2, 0, self.error.text, Color.IMPORTANT)
                else:
                    self.display_line(self.screen.y_max - 2, 0, MSG_ERRORS, Color.IMPORTANT)
            else:
                self.display_line(self.screen.y_max - 2, 0, self.error.text, Color.HINTS)

            self.error.clear_buffer()

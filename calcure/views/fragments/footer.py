from calcure.base_view import View
from calcure.colors import Color
from calcure.configuration import AppState
from calcure.dialogues import clear_line
from calcure.singletons import global_config
from calcure.translations.en import JOURNAL_HINT

class FooterView(View):
    """Display the footer with keybinding"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        if not global_config.SHOW_KEYBINDINGS: 
            return
        clear_line(self.stdscr, self.screen.y_max - 1)
        if self.screen.state == AppState.JOURNAL:
            hint = JOURNAL_HINT
            self.display_line(self.screen.y_max - 1, 0, hint, Color.HINTS)

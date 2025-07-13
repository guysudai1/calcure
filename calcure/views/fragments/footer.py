from calcure.base_view import View
from calcure.colors import Color
from calcure.configuration import AppState
from calcure.dialogues import clear_line
from calcure.singletons import global_config
from calcure.translations.en import ARCHIVE_HINT, JOURNAL_HINT, WORKSPACE_HINT

class FooterView(View):
    """Display the footer with keybinding"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def get_screen_state(self):
        all_states = "|"
        for i, state in enumerate(AppState, start=1):
            if self.screen.state == state:
                all_states += f" *{i}* |"
            else:
                all_states += f" {i} ({state.name.lower()}) |"
        return all_states
    
    def render(self):
        """Render this view on the screen"""
        if not global_config.SHOW_KEYBINDINGS.value: 
            return
        clear_line(self.stdscr, self.screen.y_max - 1)

        hints = self.get_screen_state()

        if self.screen.state == AppState.JOURNAL:
            hints += "   " + JOURNAL_HINT
        if self.screen.state == AppState.ARCHIVE:
            hints += "   " + ARCHIVE_HINT
        if self.screen.state == AppState.WIZARD:
            hints += "   " + WORKSPACE_HINT
        self.display_line(self.screen.y_max - 1, 0, hints, Color.HINTS)
        


from calcuresu.base_view import View
from calcuresu.colors import Color
from calcuresu.configuration import AppState
from calcuresu.dialogues import clear_line
from calcuresu.singletons import global_config
from calcuresu.translations.en import ARCHIVE_HINT, JOURNAL_HINT, WORKSPACE_HINT

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
        
        if not self.screen.need_refresh:
            return

        clear_line(self.stdscr, self.screen.y_max - 1)

        hints = self.get_screen_state()
 
        if self.screen.state == AppState.JOURNAL:
            keybinds = JOURNAL_HINT
        if self.screen.state == AppState.ARCHIVE:
            keybinds = ARCHIVE_HINT
        if self.screen.state == AppState.WIZARD:
            keybinds = WORKSPACE_HINT
        else:
            keybinds = ""
        self.display_line(self.screen.y_max - 3, (self.screen.x_max - len(keybinds)) // 2, keybinds, Color.HINTS)
        self.display_line(self.screen.y_max - 1, (self.screen.x_max - len(hints)) // 2, hints, Color.HINTS)
        


from calcuresu.base_view import View
from calcuresu.colors import Color
from calcuresu.consts import VERSION
from calcuresu.screen import Screen
from calcuresu.singletons import global_config
from calcuresu.translations.en import KEYS_ARCHIVE, KEYS_GENERAL, KEYS_JOURNAL, KEYS_WORKSPACE, MSG_INFO, MSG_NAME, MSG_SITE, TITLE_KEYS_ARCHIVE, TITLE_KEYS_GENERAL, TITLE_KEYS_JOURNAL, TITLE_KEYS_WORKSPACE

class HelpScreenView(View):
    """Help screen displaying information about keybindings"""

    MAX_BINDINGS_X_SIZE = 50

    def __init__(self, stdscr, y, x, screen: Screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def calibrate_position(self):
        """Depending on the screen space calculate the best position"""
        self.y_max, self.x_max = self.stdscr.getmaxyx()
        
        self.x = 2
        self.y = 0

    def render(self):
        """Draw the help screen"""

        if not self.screen.need_refresh:
            return

        self.calibrate_position()
        self.stdscr.clear()
        self.fill_background()

        # Left column:
        title_value = f"{MSG_NAME} {VERSION}"
        self.display_line(self.y, self.x_max // 2 - len(title_value), title_value, Color.ACTIVE_PANE, global_config.BOLD_TITLE.value, global_config.UNDERLINED_TITLE.value)

        """
        General keybindings
        """
        title_x_offset = self.x + 8 
        self.display_line(self.y + 2, title_x_offset, TITLE_KEYS_GENERAL, Color.TITLE, global_config.BOLD_TITLE.value, global_config.UNDERLINED_TITLE.value)
        for index, key in enumerate(KEYS_GENERAL):
            item_height = self.y + index + 3
            self.display_line(item_height, self.x, key, Color.ACTIVE_PANE)
            self.display_line(item_height,  title_x_offset, KEYS_GENERAL[key], Color.HINTS)
        self.stdscr.refresh()
        
        """
        Journal keybindings
        """
        title_x_offset += self.MAX_BINDINGS_X_SIZE
        base_index = 0
        self.display_line(self.y + 2, title_x_offset, TITLE_KEYS_JOURNAL, Color.TITLE, global_config.BOLD_TITLE.value, global_config.UNDERLINED_TITLE.value)
        for index, key in enumerate(KEYS_JOURNAL):
            item_height = self.y + (index - base_index) + 3
            if item_height >= self.y_max - 4:
                # Split the GUI
                title_x_offset += self.MAX_BINDINGS_X_SIZE
                base_index = index
                item_height = self.y + (index - base_index) + 3
            self.display_line(item_height, title_x_offset - 8, key, Color.ACTIVE_PANE)
            self.display_line(item_height,  title_x_offset, KEYS_JOURNAL[key], Color.HINTS)

        """
        Archive keybindings
        """
        title_x_offset += self.MAX_BINDINGS_X_SIZE
        base_index = 0
        self.display_line(self.y + 2, title_x_offset, TITLE_KEYS_ARCHIVE, Color.TITLE, global_config.BOLD_TITLE.value, global_config.UNDERLINED_TITLE.value)
        for index, key in enumerate(KEYS_ARCHIVE):
            item_height = self.y + (index - base_index) + 3
            if item_height >= self.y_max - 4:
                # Split the GUI
                title_x_offset += self.MAX_BINDINGS_X_SIZE
                base_index = index
                item_height = self.y + (index - base_index) + 3
            self.display_line(item_height, title_x_offset - 8, key, Color.ACTIVE_PANE)
            self.display_line(item_height,  title_x_offset, KEYS_ARCHIVE[key], Color.HINTS)
            

        """
        Workspace keybindings (same X as archive keybindings)
        """
        base_index = 0
        self.display_line(self.y + len(KEYS_ARCHIVE) + 4 + 2, title_x_offset, TITLE_KEYS_WORKSPACE, Color.TITLE, global_config.BOLD_TITLE.value, global_config.UNDERLINED_TITLE.value)
        for index, key in enumerate(KEYS_WORKSPACE):
            item_height = self.y + (index - base_index) + 3 + len(KEYS_ARCHIVE) + 4
            if item_height >= self.y_max - 4:
                # Split the GUI
                title_x_offset += self.MAX_BINDINGS_X_SIZE
                base_index = index
                item_height = self.y + (index - base_index) + 3
            self.display_line(item_height, title_x_offset - 8, key, Color.ACTIVE_PANE)
            self.display_line(item_height,  title_x_offset, KEYS_WORKSPACE[key], Color.HINTS)
        
        # Additional info:
        additional_info_base_y = self.y_max - 3
        additional_info_base_x = self.x_max // 2
        self.display_line(additional_info_base_y, additional_info_base_x - len(MSG_INFO) // 2, MSG_INFO, Color.HINTS)
        self.display_line(additional_info_base_y + 1, additional_info_base_x - len(MSG_SITE) // 2, MSG_SITE, Color.TITLE)

"""Module that controls the overall state of the program screen"""

import datetime
import logging

from calcure.configuration import Config
from calcure.consts import AppState


class Screen:
    """Main state of the program that describes what is displayed and how"""
    def __init__(self, stdscr, global_config: Config):
        self.stdscr = stdscr
        self.privacy = global_config.PRIVACY_MODE
        self._state = global_config.DEFAULT_VIEW
        self.right_pane_percentage = global_config.RIGHT_PANE_PERCENTAGE
        self.currently_drawn = self.state
        self.selection_mode = False
        self.refresh_now = True
        self.reload_data = False
        self.delayed_action = False
        self.key: str|None = None
        self.day = self.today.day
        self.month = self.today.month
        self.year = self.today.year
        self.offset = 0
        

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_state):
        self.offset = 0
        self._state = new_state
        
    @property
    def is_active_pane(self):
        """Return True if currently drawn pane in the active one"""
        return self.state == self.currently_drawn

    @property
    def y_max(self):
        """Get maximum size of the screen"""
        y_max, _ = self.stdscr.getmaxyx()
        return y_max

    @property
    def journal_pane_width(self):
        """Calculate the width of the right pane if the value is adequate"""
        _, x_max = self.stdscr.getmaxyx()
        if 5 < self.right_pane_percentage < 95:
            return int(x_max//(100/self.right_pane_percentage))
        return x_max//4

    @property
    def x_max(self):
        """Calculate the right boundary of the screen"""
        _, x_max = self.stdscr.getmaxyx()
        return x_max

    @property
    def x_min(self):
        """Calculate the left boundary of the screen"""
        _, x_max = self.stdscr.getmaxyx()
        return 0

    def change_offset_forwards(self, step_count: int):
        self.offset += step_count

    def change_offset_backwards(self, step_count: int):
        self.offset = max(0, self.offset - step_count)

    @property
    def date(self):
        """Return displayed date in datetime format"""
        return datetime.date(self.year, self.month, self.day)

    @property
    def today(self):
        """Return todays's date in datetime format"""
        return datetime.date.today()

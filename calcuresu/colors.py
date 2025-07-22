"""Module that provides few converter functions"""

import curses
from enum import Enum, auto

from calcuresu.configuration import Config




class Color(Enum):
    """Colors read from user config"""
    HINTS = auto()
    PROMPTS = auto()
    TITLE = auto()
    DONE = auto()
    ERROR = auto()
    TIMER = auto()
    TIMER_PAUSED = auto()
    TIME = auto()
    HEADER = auto()
    ACTIVE_PANE = auto()
    EMPTY = auto()
    DEADLINES = auto()

    """
    Task colors
    """
    NOT_STARTED = auto()
    WIP = auto()
    CURRENT_MISSION = auto()
    WAITING = auto()
    IMPORTANCE = auto()

    """
    Workspace colors
    """
    WORKSPACE = auto()

def initialize_colors(global_config: Config):
    """Define all the color pairs"""
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(Color.HINTS.value, global_config.COLOR_HINTS.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.PROMPTS.value, global_config.COLOR_PROMPTS.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.TIMER.value, global_config.COLOR_TIMER.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.TIMER_PAUSED.value, global_config.COLOR_TIMER_PAUSED.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.TIME.value, global_config.COLOR_TIME.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.HEADER.value, global_config.COLOR_HEADER.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.ACTIVE_PANE.value, global_config.COLOR_ACTIVE_PANE.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.EMPTY.value, global_config.COLOR_BACKGROUND.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.DEADLINES.value, global_config.COLOR_DEADLINES.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.ERROR.value, global_config.COLOR_ERROR.value, global_config.COLOR_BACKGROUND.value)

    """
    Task Journal Colors
    """
    curses.init_pair(Color.NOT_STARTED.value, global_config.COLOR_NOT_STARTED.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.WIP.value, global_config.COLOR_WIP.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.WAITING.value, global_config.COLOR_WAITING.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.CURRENT_MISSION.value, global_config.COLOR_CURRENT_MISSION.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.DONE.value, global_config.COLOR_DONE.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.IMPORTANCE.value, global_config.COLOR_IMPORTANCE.value, global_config.COLOR_BACKGROUND.value)
    curses.init_pair(Color.TITLE.value, global_config.COLOR_TITLE.value, global_config.COLOR_BACKGROUND.value)

    """
    Workspace Colors
    """
    curses.init_pair(Color.WORKSPACE.value, global_config.COLOR_WORKSPACE.value, global_config.COLOR_BACKGROUND.value)


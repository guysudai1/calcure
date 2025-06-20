"""Module that provides few converter functions"""

import curses
from enum import Enum, auto

from calcure.configuration import Config




class Color(Enum):
    """Colors read from user config"""
    HINTS = auto()
    PROMPTS = auto()
    CONFIRMATIONS = auto()
    TITLE = auto()
    TODO = auto()
    DONE = auto()
    IMPORTANT = auto()
    TIMER = auto()
    TIMER_PAUSED = auto()
    TIME = auto()
    UNIMPORTANT = auto()
    CALENDAR_HEADER = auto()
    ACTIVE_PANE = auto()
    SEPARATOR = auto()
    EMPTY = auto()
    CALENDAR_BORDER = auto()
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

    curses.init_pair(Color.HINTS.value, global_config.COLOR_HINTS, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.PROMPTS.value, global_config.COLOR_PROMPTS, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.CONFIRMATIONS.value, global_config.COLOR_CONFIRMATIONS, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.TIMER.value, global_config.COLOR_TIMER, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.TIMER_PAUSED.value, global_config.COLOR_TIMER_PAUSED, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.TIME.value, global_config.COLOR_TIME, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.CALENDAR_HEADER.value, global_config.COLOR_CALENDAR_HEADER, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.ACTIVE_PANE.value, global_config.COLOR_ACTIVE_PANE, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.SEPARATOR.value, global_config.COLOR_SEPARATOR, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.EMPTY.value, global_config.COLOR_BACKGROUND, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.CALENDAR_BORDER.value, global_config.COLOR_CALENDAR_BORDER, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.DEADLINES.value, global_config.COLOR_DEADLINES, global_config.COLOR_BACKGROUND)

    """
    Task Journal Colors
    """
    curses.init_pair(Color.NOT_STARTED.value, global_config.COLOR_NOT_STARTED, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.WIP.value, global_config.COLOR_WIP, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.WAITING.value, global_config.COLOR_WAITING, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.CURRENT_MISSION.value, global_config.COLOR_CURRENT_MISSION, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.DONE.value, global_config.COLOR_DONE, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.IMPORTANCE.value, global_config.COLOR_IMPORTANCE, global_config.COLOR_BACKGROUND)
    curses.init_pair(Color.TITLE.value, global_config.COLOR_TITLE, global_config.COLOR_BACKGROUND)

    """
    Workspace Colors
    """
    curses.init_pair(Color.WORKSPACE.value, global_config.COLOR_WORKSPACE, global_config.COLOR_BACKGROUND)


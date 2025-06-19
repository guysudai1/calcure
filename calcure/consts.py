import enum


VERSION = "3.2.1"


class AppState(enum.Enum):
    """Possible focus states of the application"""
    JOURNAL = 1
    HELP = 2
    EXIT = 3
    WELCOME = 4


class Status(enum.Enum):
    """Status of tasks"""
    NOT_STARTED = enum.auto()
    WIP = enum.auto()
    CURRENT_MISSION = enum.auto()
    WAITING = enum.auto()
    DONE = enum.auto()

class Importance(enum.Enum):
    """ Task Importance Levels """
    UNDECIDED = 0
    OPTIONAL_1 = 1
    OPTIONAL_2 = 2

    LOW_1 = 3 # nice to have
    LOW_2 = 4 # nice to have

    MEDIUM_1 = 5 # to do in the far future
    MEDIUM_2 = 6 # to do in the far future

    HIGH_1 = 7 # to do in the near future
    HIGH_2 = 8 # to do in the near future

    CRITICAL_1 = 9 # must be done asap
    CRITICAL_2 = 10 # must be done asap


class CursesColor(enum.IntEnum):
    # Basic Colors (0-7)
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    # Bright Colors (8-15)
    LIGHT_BLACK = 8
    LIGHT_RED = 9
    LIGHT_GREEN = 10
    LIGHT_YELLOW = 11
    LIGHT_BLUE = 12
    LIGHT_MAGENTA = 13
    LIGHT_CYAN = 14
    LIGHT_WHITE = 15
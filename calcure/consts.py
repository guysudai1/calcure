import enum


VERSION = "3.2.1"


class AppState(enum.Enum):
    """Possible focus states of the application"""
    JOURNAL = 1
    HELP = 2
    EXIT = 3
    WELCOME = 4


class Status(enum.Enum):
    """Status of events and tasks"""
    NORMAL = 1
    DONE = 2
    IMPORTANT = 3
    UNIMPORTANT = 4
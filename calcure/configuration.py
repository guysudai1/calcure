"""This module creates and loads user config file"""

import configparser
import sys
import getopt
import logging
import datetime
from pathlib import Path

from calcure.consts import AppState, CursesColor
from calcure.prompt import IconCompleter


class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        self.home_path = Path.home()
        self.config_folder = self.home_path / ".config" / "calcure"
        self.config_file = self.config_folder / "config.ini"
        self.log_file = self.config_folder / "info.log"
        self.is_first_run= True

        # Create config folder:
        self.config_folder.mkdir(exist_ok=True)

        # Read config file:
        self.create_config_file()
        self.read_config_file_from_user_arguments()
        self.read_config_file()
        self.read_parameters_from_user_arguments()


    def shorten_path(self, path):
        """Replace home part of paths with tilde"""
        if str(path).startswith(str(self.home_path)):
            return str(path).replace(str(self.home_path), "~", 1)
        else:
            return str(path)


    def create_config_file(self):
        """Create config.ini file if it does not exist"""

        if self.config_file.exists():
            self.is_first_run = False
            return

        conf = configparser.ConfigParser()
        conf["Parameters"] = {
                "folder_with_datafiles":     self.shorten_path(self.config_folder),
                "log_file":                  self.shorten_path(self.log_file),
                "language":                  "en",
                "default_view":              "journal",
                "default_calendar_view":     "monthly",
                "show_keybindings":          "Yes",
                "privacy_mode":              "No",
                "cut_titles_by_cell_length": "No",
                "ask_confirmations":         "Yes",
                "ask_confirmation_to_quit":  "Yes",
                "add_to_archive_on_delete":  "Yes",
                "use_unicode_icons":         "Yes",
                "show_current_time":         "No",
                "show_holidays":             "Yes",
                "show_nothing_planned":      "Yes",
                "one_timer_at_a_time":       "No",
                "start_week_day":            "1",
                "weekend_days":              "6,7",
                "refresh_interval":          "1",
                "save_interval":             "10",
                "data_reload_interval":      "0",
                "split_screen":              "No",
                "right_pane_percentage":     "25",
                "journal_header":            "JOURNAL",
                "archive_header":            "ARCHIVE",
                "event_icon":                "•",
                "privacy_icon":              "•",
                "done_icon":                 "✔",
                "todo_icon":                 "•",
                "important_icon":            "‣",
                "separator_icon":            "│",
                "deadline_icon":             "⚑",
                }

        conf["Colors"] = {
                "color_hints":           "7",
                "color_prompts":         "7",
                "color_confirmations":   "1",
                "color_not_started":     "38",
                "color_wip":             "173",
                "color_current_mission": "57",
                "color_waiting":         "230",
                "color_done":            "40",
                "color_title":           "4",
                "color_calendar_header": "4",
                "color_timer":           "2",
                "color_timer_paused":    "7",
                "color_time":            "7",
                "color_deadlines":       "3",
                "color_active_pane":     "2",
                "color_separator":       "7",
                "color_calendar_border": "7",
                "color_background":      "-1",
                }

        conf["Styles"] = {
                "bold_title":               "No",
                "bold_active_pane":         "No",
                "underlined_title":         "No",
                "underlined_active_pane":   "No",
                "strikethrough_done":       "No",
                }

        conf["Event icons"] = {
                "travel":      "✈",
                "plane":       "✈",
                "voyage":      "✈",
                "flight":      "✈",
                "airport":     "✈",
                "trip":        "🏕",
                "vacation":    "⛱",
                "holiday":     "⛱",
                "day-off":     "⛱",
                "hair":        "✂",
                "barber":      "✂",
                "beauty":      "✂",
                "nails":       "✂",
                "game":        "♟",
                "match":       "♟",
                "play":        "♟",
                "interview":   "🎙️",
                "conference":  "🎙️",
                "talk":        "🎙️",
                "dating":      "♥",
                "concert":     "♪",
                "dance":       "♪",
                "music":       "♪",
                "rehearsal":   "♪",
                "call":        "🕻",
                "zoom":        "🕻",
                "deadline":    "⚑",
                "over":        "⚑",
                "finish":      "⚑",
                "end":         "⚑",
                "doctor":      "✚",
                "dentist":     "✚",
                "medical":     "✚",
                "hospital":    "✚",
                "party":       "☘",
                "bar":         "☘",
                "museum":      "⛬",
                "meet":        "⛬",
                "sport":       "⛷",
                "gym":         "🏋",
                "training":    "⛷",
                "email":       "✉",
                "letter":      "✉",
                }

        with open(self.config_file, 'w', encoding="utf-8") as f:
            conf.write(f)


    def read_config_file(self):
        """Read user config.ini file and assign values to all the global variables"""
        try:
            conf = configparser.ConfigParser()
            conf.read(self.config_file, 'utf-8')

            # Reading default view:
            self.DEFAULT_VIEW = AppState.JOURNAL
            
            # Calendar settings:
            self.SHOW_KEYBINDINGS          = conf.getboolean("Parameters", "show_keybindings", fallback=True)
            self.ASK_CONFIRMATIONS         = conf.getboolean("Parameters", "ask_confirmations", fallback=True)
            self.ASK_CONFIRMATION_TO_QUIT  = conf.getboolean("Parameters", "ask_confirmation_to_quit", fallback=True)
            self.ADD_TO_ARCHIVE_ON_DELETE  = conf.getboolean("Parameters", "add_to_archive_on_delete", fallback=True)
            self.SHOW_CURRENT_TIME         = conf.getboolean("Parameters", "show_current_time", fallback=True)
            self.DISPLAY_ICONS             = conf.getboolean("Parameters", "use_unicode_icons", fallback=True)
            self.PRIVACY_MODE              = conf.getboolean("Parameters", "privacy_mode", fallback=False)
            self.SPLIT_SCREEN              = conf.getboolean("Parameters", "split_screen", fallback=False)
            self.SHOW_NOTHING_PLANNED      = conf.getboolean("Parameters", "show_nothing_planned", fallback=True)
            self.LANG                      = conf.get("Parameters", "language", fallback="en")
            self.LOG_FILE                  = conf.get("Parameters", "log_file", fallback=self.log_file)
            self.LOG_FILE                  = Path(self.LOG_FILE).expanduser()

            # Journal settings:
            self.JOURNAL_HEADER        = conf.get("Parameters", "journal_header", fallback="JOURNAL")
            self.ARCHIVE_HEADER        = conf.get("Parameters", "archive_header", fallback="ARCHIVE")
            self.SHOW_KEYBINDINGS      = conf.getboolean("Parameters", "show_keybindings", fallback=True)
            self.DONE_ICON             = conf.get("Parameters", "done_icon", fallback="✔") if self.DISPLAY_ICONS else "×"
            self.TODO_ICON             = conf.get("Parameters", "todo_icon", fallback="•") if self.DISPLAY_ICONS else "·"
            self.IMPORTANT_ICON        = conf.get("Parameters", "important_icon", fallback="‣") if self.DISPLAY_ICONS else "!"
            self.REFRESH_INTERVAL      = int(conf.get("Parameters", "refresh_interval", fallback=1))
            self.DATA_RELOAD_INTERVAL  = int(conf.get("Parameters", "data_reload_interval", fallback=0))
            self.RIGHT_PANE_PERCENTAGE = int(conf.get("Parameters", "right_pane_percentage", fallback=25))
            self.ONE_TIMER_AT_A_TIME   = conf.getboolean("Parameters", "one_timer_at_a_time", fallback=False)
            self.COLLAPSED_ICON = "\u21AA"
            self.JOURNAL_SAVE_INTERVAL        = float(conf.get("Parameters", "save_interval", fallback=10))

            # Calendar colors:
            self.COLOR_HINTS           = int(conf.get("Colors", "color_hints", fallback=CursesColor.WHITE.value))
            self.COLOR_PROMPTS         = int(conf.get("Colors", "color_prompts", fallback=CursesColor.WHITE.value))
            self.COLOR_DEADLINES       = int(conf.get("Colors", "color_deadlines", fallback=CursesColor.YELLOW.value))
            self.COLOR_CONFIRMATIONS   = int(conf.get("Colors", "color_confirmations", fallback=CursesColor.RED.value))
            self.COLOR_TIMER           = int(conf.get("Colors", "color_timer", fallback=CursesColor.GREEN.value))
            self.COLOR_TIMER_PAUSED    = int(conf.get("Colors", "color_timer_paused", fallback=CursesColor.WHITE.value))
            self.COLOR_TIME            = int(conf.get("Colors", "color_time", fallback=CursesColor.WHITE.value))
            self.COLOR_BACKGROUND      = int(conf.get("Colors", "color_background", fallback=-CursesColor.RED.value))
            self.COLOR_CALENDAR_HEADER = int(conf.get("Colors", "color_calendar_header", fallback=CursesColor.BLUE.value))
            self.COLOR_ACTIVE_PANE     = int(conf.get("Colors", "color_active_pane", fallback=CursesColor.GREEN.value))
            self.COLOR_SEPARATOR       = int(conf.get("Colors", "color_separator", fallback=CursesColor.WHITE.value))
            self.COLOR_CALENDAR_BORDER = int(conf.get("Colors", "color_calendar_border", fallback=CursesColor.WHITE.value))

            # Journal colors:
            self.COLOR_NOT_STARTED           = int(conf.get("Colors", "color_not_started", fallback=38))
            self.COLOR_WIP      = int(conf.get("Colors", "color_wip", fallback=173)) 
            self.COLOR_CURRENT_MISSION    = int(conf.get("Colors", "color_current_mission", fallback=57))
            self.COLOR_WAITING    = int(conf.get("Colors", "color_waiting", fallback=230))
            self.COLOR_DONE           = int(conf.get("Colors", "color_done", fallback=40))
            self.COLOR_IMPORTANCE           = int(conf.get("Colors", "color_importance", fallback=231))
            
            self.COLOR_TITLE          = int(conf.get("Colors", "color_title", fallback=CursesColor.RED.value)) # TODO: Pick color

            # Font styles:
            self.BOLD_TITLE               = conf.getboolean("Styles", "bold_title", fallback=False)
            self.BOLD_ACTIVE_PANE         = conf.getboolean("Styles", "bold_active_pane", fallback=False)
            self.UNDERLINED_TITLE         = conf.getboolean("Styles", "underlined_title", fallback=False)
            self.UNDERLINED_ACTIVE_PANE   = conf.getboolean("Styles", "underlined_active_pane", fallback=False)
            self.STRIKETHROUGH_DONE       = conf.getboolean("Styles", "strikethrough_done", fallback=False)

            # Icons:
            self.PRIVACY_ICON     = conf.get("Parameters", "privacy_icon", fallback="•") if self.DISPLAY_ICONS else "·"
            self.SEPARATOR_ICON   = conf.get("Parameters", "separator_icon", fallback="│")
            self.DEADLINE_ICON    = conf.get("Parameters", "deadline_icon", fallback="⚑") if self.DISPLAY_ICONS else "·"
            try:
                self.CUSTOM_ICONS = {word: icon for (word, icon) in conf.items("Event icons")}
            except configparser.NoSectionError:
                self.CUSTOM_ICONS = {}

            self.icon_completer = IconCompleter(list(self.CUSTOM_ICONS.items()))
            
            self.data_folder = conf.get("Parameters", "folder_with_datafiles", fallback=self.config_folder)
            self.data_folder = Path(self.data_folder).expanduser()
            self.TASKS_FILE = self.data_folder / "tasks"
            self.ARCHIVE_FILE = self.data_folder / "archive_tasks"

        except Exception:
            ERR_FILE1 = "Looks like there is a problem in your config.ini file. Perhaps you edited it and entered a wrong line. "
            ERR_FILE2 = "Try removing your config.ini file and run the program again, it will create a fresh working config file."
            logging.error(ERR_FILE1 + ERR_FILE2)
            exit()


    def read_config_file_from_user_arguments(self):
        """Read user config.ini location from user arguments"""
        try:
            opts, _ = getopt.getopt(sys.argv[1:], "pjchv", ["folder=", "config="])
            for opt, arg in opts:
                if opt in "--config":
                    self.config_file = Path(arg).expanduser()
                    if not self.config_file.exists():
                        self.create_config_file()
        except getopt.GetoptError:
            pass


    def read_parameters_from_user_arguments(self):
        """Read user arguments that were provided at the run. This values take priority over config.ini"""
        try:
            opts, _ = getopt.getopt(sys.argv[1:],"pjhvid",["folder=", "config=", "task=", "event="])
            for opt, arg in opts:
                if opt in '--folder':
                    self.data_folder = Path(arg).expanduser()
                    self.data_folder.mkdir(exist_ok=True)
                    self.TASKS_FILE = self.data_folder / "tasks.csv"
                elif opt == '-p':
                    self.PRIVACY_MODE = True
                elif opt == '-j':
                    self.DEFAULT_VIEW = AppState.JOURNAL
                elif opt in ('-h'):
                    self.DEFAULT_VIEW = AppState.HELP
                elif opt in ('-v'):
                    self.DEFAULT_VIEW = AppState.EXIT
                    print ('Calcure - version 3.2.1')
        except getopt.GetoptError as e_message:
            logging.error("Invalid user arguments. %s", e_message)
            pass


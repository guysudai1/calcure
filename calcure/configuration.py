"""This module creates and loads user config file"""

import configparser
from enum import Enum
import sys
import getopt
import logging
import datetime
from pathlib import Path
from typing import Any

from calcure.consts import AppState, CursesColor
from calcure.prompt import IconCompleter

class ConfigType(Enum):
    BOOL = 0
    STRING = 1
    INT = 2
    PATH = 3
    FLOAT = 4

class ConfigItem:
    def __init__(self, section: str, option: str, item_type: ConfigType, value: Any, default: Any) -> None:
        self.section = section
        self.option = option
        self.value = value
        self.type = item_type
        self.default = default


    @classmethod
    def from_config(cls, conf: configparser.ConfigParser, section: str, option: str, item_type: ConfigType, default: Any):
        match item_type:
            case ConfigType.BOOL:
                value = conf.getboolean(section, option, fallback=default)
            case ConfigType.STRING:
                value = conf.get(section, option, fallback=default)
            case ConfigType.INT:
                value = int(conf.get(section, option, fallback=default))
            case ConfigType.PATH:
                value = Path(conf.get(section, option, fallback=default)).expanduser()
            case ConfigType.FLOAT:
                value = float(conf.get(section, option, fallback=default))
            case _:
                raise Exception()
            
        return ConfigItem(section, option, item_type, value, default)


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
        self.read_config_file_from_user_arguments()
        self.read_config_file()
        self.create_default_config_file()
        import ipdb; ipdb.set_trace()


    def shorten_path(self, path):
        """Replace home part of paths with tilde"""
        if str(path).startswith(str(self.home_path)):
            return str(path).replace(str(self.home_path), "~", 1)
        else:
            return str(path)


    def create_default_config_file(self):
        """Create config.ini file if it does not exist"""

        self.is_first_run = not self.config_file.exists()
        if not self.is_first_run:
            return

        all_default_setting_keys = [x for x in dir(self) if x == x.upper()]
        all_default_settings = {}
        for k in all_default_setting_keys:
            all_default_settings[k] = getattr(self, k)
        
        conf = configparser.ConfigParser()

        extra_fun_icons = {

        }

        with open(self.config_file, 'w', encoding="utf-8") as f:
            conf.write(f)


    def read_config_file(self):
        """Read user config.ini file and assign values to all the global variables"""
        try:
            conf = configparser.ConfigParser()
            conf.read(self.config_file, 'utf-8')

            # Reading default view:
            self.DEFAULT_VIEW = AppState.WIZARD
            
            self.SHOW_KEYBINDINGS          = ConfigItem.from_config(conf, "Parameters", "show_keybindings", ConfigType.BOOL, True) 
            self.ASK_CONFIRMATION_TO_QUIT  = ConfigItem.from_config(conf, "Parameters", "ask_confirmation_to_quit", ConfigType.BOOL, True)
            self.SHOW_CURRENT_TIME         = ConfigItem.from_config(conf, "Parameters", "show_current_time", ConfigType.BOOL, True)
            self.DISPLAY_ICONS             = ConfigItem.from_config(conf, "Parameters", "use_unicode_icons", ConfigType.BOOL, True)
            self.REFRESH_INTERVAL          = ConfigItem.from_config(conf, "Parameters", "refresh_interval", ConfigType.INT, 1)
            self.SHOW_NOTHING_PLANNED      = ConfigItem.from_config(conf, "Parameters", "show_nothing_planned", ConfigType.BOOL, True)
            self.LANG                      = ConfigItem.from_config(conf, "Parameters", "language", ConfigType.STRING, "en")
            self.LOG_FILE                  = ConfigItem.from_config(conf, "Parameters", "log_file", ConfigType.PATH, self.log_file)

            # Archive settings
            self.ADD_TO_ARCHIVE_ON_DELETE  = ConfigItem.from_config(conf, "Parameters", "add_to_archive_on_delete", ConfigType.BOOL, True)
            self.ARCHIVE_HEADER        = ConfigItem.from_config(conf, "Parameters", "archive_header", ConfigType.STRING, "ARCHIVE")

            # Journal settings
            self.JOURNAL_HEADER        = ConfigItem.from_config(conf, "Parameters", "journal_header", ConfigType.STRING, "JOURNAL")

            # Icon settings
            self.DONE_ICON             = ConfigItem.from_config(conf, "Parameters", "done_icon", ConfigType.STRING, "✔") if self.DISPLAY_ICONS else "×"
            self.TODO_ICON             = ConfigItem.from_config(conf, "Parameters", "todo_icon", ConfigType.STRING, "•") if self.DISPLAY_ICONS else "·"
            self.IMPORTANT_ICON        = ConfigItem.from_config(conf, "Parameters", "important_icon", ConfigType.STRING, "‣") if self.DISPLAY_ICONS else "!"
            self.COLLAPSED_ICON = ConfigItem.from_config(conf, "Parameters", "collapsed_icon", ConfigType.STRING, "\u21AA") if self.DISPLAY_ICONS else "~"
            self.PRIVACY_ICON     = ConfigItem.from_config(conf, "Parameters", "privacy_icon", ConfigType.STRING, "•") if self.DISPLAY_ICONS else "·"
            self.SEPARATOR_ICON   = ConfigItem.from_config(conf, "Parameters", "separator_icon", ConfigType.STRING, "│")
            self.EXTRA_INFO_ICON   = ConfigItem.from_config(conf, "Parameters", "extra_info_icon", ConfigType.STRING, "💾")
            self.DEADLINE_ICON    = ConfigItem.from_config(conf, "Parameters", "deadline_icon", ConfigType.STRING, "⚑") if self.DISPLAY_ICONS else "·"

            # Custom icon settings
            try:
                # TODO: Implement custom icons
                self.CUSTOM_ICONS = {word: icon for (word, icon) in conf.items("Event icons")}
            except configparser.NoSectionError:
                self.CUSTOM_ICONS = {}
            self.icon_completer = IconCompleter(list(self.CUSTOM_ICONS.items()))

            # File save settings
            self.LOCK_ACQUIRE_TIMEOUT      = ConfigItem.from_config(conf, "Parameters", "lock_acquire_timeout", ConfigType.INT, 600) # 10 minutes
            self.LOCK_LIFETIME             = ConfigItem.from_config(conf, "Parameters", "lock_lifetime", ConfigType.INT, 580) # 9 minutes and 40 seconds
            assert self.LOCK_LIFETIME.value < self.LOCK_ACQUIRE_TIMEOUT.value, "If the lifetime is smaller than the acquiriation timeout then we might not catch the lock"
            self.JOURNAL_SAVE_INTERVAL     = ConfigItem.from_config(conf, "Parameters", "save_interval", ConfigType.FLOAT, 10)

            # Color settings
            self.COLOR_HINTS           = int(conf.get("Colors", "color_hints", fallback=CursesColor.WHITE.value))
            self.COLOR_PROMPTS         = int(conf.get("Colors", "color_prompts", fallback=CursesColor.WHITE.value))
            self.COLOR_DEADLINES       = int(conf.get("Colors", "color_deadlines", fallback=CursesColor.YELLOW.value))
            self.COLOR_CONFIRMATIONS   = int(conf.get("Colors", "color_confirmations", fallback=CursesColor.RED.value))
            self.COLOR_TIMER           = int(conf.get("Colors", "color_timer", fallback=CursesColor.GREEN.value))
            self.COLOR_TIMER_PAUSED    = int(conf.get("Colors", "color_timer_paused", fallback=CursesColor.WHITE.value))
            self.COLOR_TIME            = int(conf.get("Colors", "color_time", fallback=CursesColor.WHITE.value))
            self.COLOR_BACKGROUND      = int(conf.get("Colors", "color_background", fallback=-CursesColor.RED.value))
            self.COLOR_HEADER = int(conf.get("Colors", "color_header", fallback=CursesColor.BLUE.value))
            self.COLOR_ACTIVE_PANE     = int(conf.get("Colors", "color_active_pane", fallback=CursesColor.GREEN.value))

            # Journal colors:
            self.COLOR_NOT_STARTED           = int(conf.get("Colors", "color_not_started", fallback=38))
            self.COLOR_WIP      = int(conf.get("Colors", "color_wip", fallback=173)) 
            self.COLOR_CURRENT_MISSION    = int(conf.get("Colors", "color_current_mission", fallback=57))
            self.COLOR_WAITING    = int(conf.get("Colors", "color_waiting", fallback=230))
            self.COLOR_DONE           = int(conf.get("Colors", "color_done", fallback=40))
            self.COLOR_IMPORTANCE           = int(conf.get("Colors", "color_importance", fallback=231))
            self.COLOR_TITLE          = int(conf.get("Colors", "color_title", fallback=CursesColor.RED.value))
            self.COLOR_WORKSPACE          = int(conf.get("Colors", "color_workspace", fallback=CursesColor.MAGENTA.value))
            
            # Font styles:
            self.BOLD_TITLE               = conf.getboolean("Styles", "bold_title", fallback=False)
            self.BOLD_ACTIVE_PANE         = conf.getboolean("Styles", "bold_active_pane", fallback=False)
            self.UNDERLINED_TITLE         = conf.getboolean("Styles", "underlined_title", fallback=False)
            self.UNDERLINED_ACTIVE_PANE   = conf.getboolean("Styles", "underlined_active_pane", fallback=False)
            self.STRIKETHROUGH_DONE       = conf.getboolean("Styles", "strikethrough_done", fallback=False)

            # File location settings            
            self.DATA_FOLDER = ConfigItem.from_config(conf, "Parameters", "folder_with_datafiles", ConfigType.PATH, self.config_folder)
            self.WORKSPACES_FILE = ConfigItem.from_config(conf, "Parameters", "workspace_file", 
                                                          ConfigType.PATH, self.DATA_FOLDER.value / "workspaces")
            self.WORKSPACES_LOCK_FILE = ConfigItem.from_config(conf, "Parameters", "workspace_lockfile",
                                                                 ConfigType.PATH, self.DATA_FOLDER.value / "workspaces.lock")

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



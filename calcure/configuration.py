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

    def __str__(self):
        return f"[{self.section}] {self.option} - {self.value}"

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
        all_default_settings: dict[Any, ConfigItem] = {}
        for k in all_default_setting_keys:
            all_default_settings[k] = getattr(self, k)
        
        conf = configparser.ConfigParser()

        for setting in all_default_settings.values():
            if not conf.has_section(setting.section):
                conf.add_section(setting.section)
            conf.set(setting.section, setting.option, str(setting.default))

        fun_default_icons = {
            "docs": "🗎",
            "talk": "👄",
            "go": "👣",
            "poop": "💩",
            "think": "💭",
            "research": "🔍"
        }
        conf.add_section("Event icons")
        for icon_name, icon in fun_default_icons.items():
            conf.set("Event icons", icon_name, icon)

        with open(self.config_file, 'w', encoding="utf-8") as f:
            conf.write(f)


    def read_config_file(self):
        """Read user config.ini file and assign values to all the global variables"""
        conf = configparser.ConfigParser()
        conf.read(self.config_file, 'utf-8')

        # Reading default view:
        self.DEFAULT_VIEW = ConfigItem.from_config(conf, "Parameters", "default_view", ConfigType.INT, AppState.WIZARD.value)
        
        self.SHOW_KEYBINDINGS          = ConfigItem.from_config(conf, "Parameters", "show_keybindings", ConfigType.BOOL, True) 
        self.SHOW_CURRENT_TIME         = ConfigItem.from_config(conf, "Parameters", "show_current_time", ConfigType.BOOL, True)
        self.REFRESH_INTERVAL          = ConfigItem.from_config(conf, "Parameters", "refresh_interval", ConfigType.INT, 1)
        self.SHOW_NOTHING_PLANNED      = ConfigItem.from_config(conf, "Parameters", "show_nothing_planned", ConfigType.BOOL, True)
        self.LOG_FILE                  = ConfigItem.from_config(conf, "Parameters", "log_file", ConfigType.PATH, self.log_file)

        # Archive settings
        self.ADD_TO_ARCHIVE_ON_DELETE  = ConfigItem.from_config(conf, "Parameters", "add_to_archive_on_delete", ConfigType.BOOL, True)
        self.ARCHIVE_HEADER        = ConfigItem.from_config(conf, "Parameters", "archive_header", ConfigType.STRING, "ARCHIVE")

        # Journal settings
        self.JOURNAL_HEADER        = ConfigItem.from_config(conf, "Parameters", "journal_header", ConfigType.STRING, "JOURNAL")

        # Icon settings
        self.DONE_ICON             = ConfigItem.from_config(conf, "Parameters", "done_icon", ConfigType.STRING, "✔") 
        self.TODO_ICON             = ConfigItem.from_config(conf, "Parameters", "todo_icon", ConfigType.STRING, "•")
        self.COLLAPSED_ICON = ConfigItem.from_config(conf, "Parameters", "collapsed_icon", ConfigType.STRING, "\u21AA")
        self.PRIVACY_ICON     = ConfigItem.from_config(conf, "Parameters", "privacy_icon", ConfigType.STRING, "•")
        self.EXTRA_INFO_ICON   = ConfigItem.from_config(conf, "Parameters", "extra_info_icon", ConfigType.STRING, "💾")

        # Custom icon settings
        try:
            self.custom_icons = {word: icon for (word, icon) in conf.items("Event icons")}
        except configparser.NoSectionError:
            self.custom_icons = {}
        self.icon_completer = IconCompleter(list(self.custom_icons.items()))

        # File save settings
        self.LOCK_ACQUIRE_TIMEOUT      = ConfigItem.from_config(conf, "Parameters", "lock_acquire_timeout", ConfigType.INT, 600) # 10 minutes
        self.LOCK_LIFETIME             = ConfigItem.from_config(conf, "Parameters", "lock_lifetime", ConfigType.INT, 580) # 9 minutes and 40 seconds
        assert self.LOCK_LIFETIME.value < self.LOCK_ACQUIRE_TIMEOUT.value, "If the lifetime is smaller than the acquiriation timeout then we might not catch the lock"
        self.JOURNAL_SAVE_INTERVAL     = ConfigItem.from_config(conf, "Parameters", "save_interval", ConfigType.FLOAT, 10)

        # Color settings
        self.COLOR_HINTS           = ConfigItem.from_config(conf, "Colors", "color_hints", ConfigType.INT, CursesColor.WHITE.value)
        self.COLOR_PROMPTS         = ConfigItem.from_config(conf, "Colors", "color_prompts", ConfigType.INT, CursesColor.WHITE.value)
        self.COLOR_DEADLINES       = ConfigItem.from_config(conf, "Colors", "color_deadlines", ConfigType.INT, CursesColor.YELLOW.value)
        self.COLOR_TIMER           = ConfigItem.from_config(conf, "Colors", "color_timer", ConfigType.INT, CursesColor.GREEN.value)
        self.COLOR_TIMER_PAUSED    = ConfigItem.from_config(conf, "Colors", "color_timer_paused", ConfigType.INT, CursesColor.WHITE.value)
        self.COLOR_TIME            = ConfigItem.from_config(conf, "Colors", "color_time", ConfigType.INT, CursesColor.WHITE.value)
        self.COLOR_BACKGROUND      = ConfigItem.from_config(conf, "Colors", "color_background", ConfigType.INT, CursesColor.BLACK.value)
        self.COLOR_HEADER = ConfigItem.from_config(conf, "Colors", "color_header", ConfigType.INT, CursesColor.BLUE.value)
        self.COLOR_ACTIVE_PANE     = ConfigItem.from_config(conf, "Colors", "color_active_pane", ConfigType.INT, CursesColor.GREEN.value)
        self.COLOR_ERROR          = ConfigItem.from_config(conf, "Colors", "color_error", ConfigType.INT, CursesColor.RED.value)

        # Journal colors:
        self.COLOR_NOT_STARTED           = ConfigItem.from_config(conf, "Colors", "color_not_started", ConfigType.INT, 38)
        self.COLOR_WIP      = ConfigItem.from_config(conf, "Colors", "color_wip", ConfigType.INT, 173) 
        self.COLOR_CURRENT_MISSION    = ConfigItem.from_config(conf, "Colors", "color_current_mission", ConfigType.INT, 57)
        self.COLOR_WAITING    = ConfigItem.from_config(conf, "Colors", "color_waiting", ConfigType.INT, 230)
        self.COLOR_DONE           = ConfigItem.from_config(conf, "Colors", "color_done", ConfigType.INT, 40)
        self.COLOR_IMPORTANCE           = ConfigItem.from_config(conf, "Colors", "color_importance", ConfigType.INT, 231)
        self.COLOR_TITLE          = ConfigItem.from_config(conf, "Colors", "color_title", ConfigType.INT, CursesColor.RED.value)
        self.COLOR_WORKSPACE          = ConfigItem.from_config(conf, "Colors", "color_workspace", ConfigType.INT, CursesColor.MAGENTA.value)
        
        # Font styles:
        self.BOLD_TITLE               = ConfigItem.from_config(conf, "Styles", "bold_title", ConfigType.BOOL, False)
        self.UNDERLINED_TITLE         = ConfigItem.from_config(conf, "Styles", "underlined_title", ConfigType.BOOL, False)
        self.STRIKETHROUGH_DONE       = ConfigItem.from_config(conf, "Styles", "strikethrough_done", ConfigType.BOOL, False)

        # File location settings            
        self.DATA_FOLDER = ConfigItem.from_config(conf, "Parameters", "folder_with_datafiles", ConfigType.PATH, self.config_folder)
        self.WORKSPACES_FILE = ConfigItem.from_config(conf, "Parameters", "workspace_file", 
                                                        ConfigType.PATH, self.DATA_FOLDER.value / "workspaces")
        self.WORKSPACES_LOCK_FILE = ConfigItem.from_config(conf, "Parameters", "workspace_lockfile",
                                                                ConfigType.PATH, self.DATA_FOLDER.value / "workspaces.lock")



    def read_config_file_from_user_arguments(self):
        """Read user config.ini location from user arguments"""
        try:
            opts, _ = getopt.getopt(sys.argv[1:], "", ["config="])
            for opt, arg in opts:
                if opt in "--config":
                    self.config_file = Path(arg).expanduser()
        except getopt.GetoptError:
            pass



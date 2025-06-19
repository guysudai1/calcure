#!/usr/bin/env python

"""This is the main module that contains views and the main logic"""

import curses
import time
import getopt
import sys
import importlib
import threading

from calcure.base_view import View
from calcure.consts import AppState
from calcure.screen import Screen
from calcure.colors import initialize_colors
from calcure.data import *
from calcure.controls import *



# Language:
from calcure.translations.en import *
from calcure.views.fragments.archive import ArchiveView
from calcure.views.fragments.error import ErrorView
from calcure.views.fragments.footer import FooterView
from calcure.views.fragments.seperator import SeparatorView
from calcure.views.screens.archive import ArchiveScreenView
from calcure.views.screens.help import HelpScreenView
from calcure.views.screens.journal import JournalScreenView
from calcure.views.screens.welcome import WelcomeScreenView


def main(stdscr) -> None:
    """Main function that runs and switches screens"""

    screen = Screen(stdscr, global_config)

    # Initialise terminal screen:
    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(False)

    initialize_colors(global_config)

    user_tasks = Tasks(global_config.TASKS_FILE)

    # Initialise screen views:
    app_view = View(stdscr, 0, 0)
    journal_screen_view = JournalScreenView(stdscr, 0, 0, user_tasks, screen)
    help_screen_view = HelpScreenView(stdscr, 0, 0, screen)
    welcome_screen_view = WelcomeScreenView(stdscr, 0, 0, screen)
    footer_view = FooterView(stdscr, 0, 0, screen)
    separator_view = SeparatorView(stdscr, 0, 0, screen)
    error_view = ErrorView(stdscr, 0, 0, screen)
    archive_view = ArchiveScreenView(stdscr, 0, 0, user_tasks, screen)

    try:
        # Show welcome screen on the first run:
        if global_config.is_first_run:
            screen.state = AppState.WELCOME
        while screen.state == AppState.WELCOME:
            welcome_screen_view.render()
            control_welcome_screen(stdscr, screen)

        # Running different screens depending on the state:
        while screen.state != AppState.EXIT:
            stdscr.clear()
            app_view.fill_background()

            # Calculate screen refresh rate:
            curses.halfdelay(200)
            if user_tasks.has_active_timer and screen.state == AppState.JOURNAL:
                curses.halfdelay(global_config.REFRESH_INTERVAL * 10)

            # Journal screen:
            if screen.state == AppState.JOURNAL:
                if screen.split:
                    separator_view.render()
                journal_screen_view.render()
                footer_view.render()
                error_view.render()
                control_journal_screen(stdscr, screen, user_tasks)

            # Help screen:
            elif screen.state == AppState.HELP:
                help_screen_view.render()
                control_help_screen(stdscr, screen)
            
            elif screen.state == AppState.ARCHIVE:
                archive_view.render()
                error_view.render()
                control_archive_screen(stdscr, screen, user_tasks)

            else:
                break
    finally:
        # Save shelve file
        user_tasks.cleanup()

        # Cleaning up before quitting:
        curses.echo()
        curses.curs_set(True)
        curses.endwin()


def cli() -> None:
    try:
        curses.wrapper(main)
    except (KeyboardInterrupt, curses.error): # Hides strange curses quitting error
        pass


if __name__ == "__main__":
    cli()

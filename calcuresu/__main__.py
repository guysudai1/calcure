#!/usr/bin/env python

"""This is the main module that contains views and the main logic"""

import curses
import time
import getopt
import sys
import importlib
import threading

from calcuresu.base_view import View
from calcuresu.consts import AppState
from calcuresu.screen import Screen
from calcuresu.colors import initialize_colors
from calcuresu.data import *
from calcuresu.controls import *



# Language:
from calcuresu.translations.en import *
from calcuresu.views.fragments.archive import ArchiveView
from calcuresu.views.fragments.error import ErrorView
from calcuresu.views.fragments.footer import FooterView
from calcuresu.views.screens.archive import ArchiveScreenView
from calcuresu.views.screens.colors import ColorScreenView
from calcuresu.views.screens.help import HelpScreenView
from calcuresu.views.screens.journal import JournalScreenView
from calcuresu.views.screens.welcome import WelcomeScreenView
from calcuresu.views.screens.wizard import WorkspaceManagerScreenView


def main(stdscr) -> None:
    """Main function that runs and switches screens"""

    screen = Screen(stdscr, global_config)

    # Initialise terminal screen:
    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(False)
    stdscr.timeout(0)
    stdscr.nodelay(True)

    initialize_colors(global_config)

    user_tasks: Tasks|None = None
    workspaces = Workspaces(global_config.WORKSPACES_FILE.value, global_config.WORKSPACES_LOCK_FILE.value)
    workspaces.initialize(stdscr, screen)

    # Initialise screen views:
    app_view = View(stdscr, 0, 0)
    journal_screen_view: JournalScreenView|None = None
    help_screen_view = HelpScreenView(stdscr, 0, 0, screen)
    welcome_screen_view = WelcomeScreenView(stdscr, 0, 0, screen)
    footer_view = FooterView(stdscr, 0, 0, screen)
    error_view = ErrorView(stdscr, 0, 0, screen)
    archive_view: ArchiveScreenView|None = None
    workspaces_view = WorkspaceManagerScreenView(stdscr, 0, 0, screen, workspaces)
    color_view = ColorScreenView(stdscr, 0, 0, screen)
    try:
        # Show welcome screen on the first run:
        if global_config.is_first_run:
            screen.state = AppState.WELCOME

        # Running different screens depending on the state:
        while screen.state != AppState.EXIT:
            if screen.resized:
                screen.current_size = stdscr.getmaxyx()
                screen.next_need_refresh = True

            screen.need_refresh = screen.next_need_refresh
            screen.next_need_refresh = False
            if screen.need_refresh:
                stdscr.clear()
                app_view.fill_background()
                stdscr.keypad(True)  # This is used for us to be able to use KEY_* again
            
            # Calculate screen refresh rate:
            curses.halfdelay(1)
            if user_tasks is not None and user_tasks.has_active_timer and screen.state == AppState.JOURNAL:
                curses.halfdelay(global_config.REFRESH_INTERVAL.value * 10)

            # Journal screen:
            if screen.state == AppState.JOURNAL:
                if journal_screen_view is not None:
                    journal_screen_view.render()
                else:
                    logging.error("Must load a workspace before going to archive. Going back to workspace manager...")
                    screen.state = AppState.WIZARD
                    screen.next_need_refresh = True

                footer_view.render()
                error_view.render()

                if user_tasks is not None and screen.state == AppState.JOURNAL:
                    if user_tasks.reopen_shelve_if_needed_locked(stdscr, screen):
                        continue

                    control_journal_screen(stdscr, screen, user_tasks)
                else:
                    # let the error be seen
                    stdscr.refresh()
                    time.sleep(0.5)

            # Help screen:
            elif screen.state == AppState.HELP:
                help_screen_view.render()
                footer_view.render()
                control_help_screen(stdscr, screen)
            elif screen.state == AppState.WELCOME:
                welcome_screen_view.render()
                footer_view.render()
                control_welcome_screen(stdscr, screen)
            elif screen.state == AppState.ARCHIVE:
                if archive_view is not None:
                    archive_view.render()
                else:
                    logging.error("Must load a workspace before going to archive. Going back to workspace manager...")
                    screen.state = AppState.WIZARD
                    screen.next_need_refresh = True
                
                footer_view.render()
                error_view.render()
                if user_tasks is not None and screen.state == AppState.ARCHIVE:
                    if user_tasks.reopen_shelve_if_needed_locked(stdscr, screen):
                        continue

                    control_archive_screen(stdscr, screen, user_tasks)
                else:
                    # let the error be seen
                    stdscr.refresh()
                    time.sleep(0.5)
                    
            elif screen.state == AppState.WIZARD:
                workspaces_view.render()
                footer_view.render()
                error_view.render()
                if workspaces.reopen_shelve_if_needed_locked(stdscr, screen):
                    continue
                
                temp_user_tasks = control_workspaces_screen(stdscr, screen, workspaces)
                if temp_user_tasks is not None:
                    user_tasks = temp_user_tasks
                    journal_screen_view = JournalScreenView(stdscr, 0, 0, user_tasks, screen)
                    archive_view = ArchiveScreenView(stdscr, 0, 0, user_tasks, screen)
                    screen.next_need_refresh = True
            elif screen.state == AppState.COLOR:
                control_color_screen(stdscr, screen)
                color_view.render()
                footer_view.render()
                stdscr.refresh()

            else:
                break

    except Exception as e:
        raise
    else:
        # Cleaning up before quitting:
        curses.echo()
        curses.curs_set(True)
        curses.endwin()
    finally:
        if user_tasks is not None:
            # Save shelve file
            user_tasks.cleanup()

        if workspaces is not None:
            # Save shelve file
            workspaces.cleanup()



def cli() -> None:
    try:
        curses.wrapper(main)
    except (KeyboardInterrupt, curses.error): # Hides strange curses quitting error
        pass


if __name__ == "__main__":
    cli()

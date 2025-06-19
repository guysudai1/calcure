"""This module contains functions that react to user input on each screen"""

import curses
import importlib

# Modules:
from calcure.classes.task import Task
from calcure.classes.timer import Timer
from calcure.consts import AppState, Status
from calcure.data import *
from calcure.dialogues import *
from calcure.configuration import Config
from calcure.screen import Screen

global_config = Config()

# Language:
from calcure.translations.en import *


def safe_run(func):
    """Decorator preventing crashes on keyboard interruption and no input"""

    def inner(stdscr, screen, *args, **kwargs):
        try:
            func(stdscr, screen, *args, **kwargs)

        # Handle keyboard interruption with ctrl+c:
        except KeyboardInterrupt:
            confirmed = ask_confirmation(stdscr, MSG_EXIT, global_config.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state

        # Prevent crash if no input:
        except curses.error:
            pass
    return inner


HEADER_FIELD_COUNT = 2

def handle_screen_transfer_keys(stdscr, screen: Screen, key: str|None):
    if key is None:
        return False

    if key == "q":
        confirmed = ask_confirmation(stdscr, MSG_EXIT, global_config.ASK_CONFIRMATION_TO_QUIT)
        if confirmed:
            screen.state = AppState.EXIT
            return True
    
    if key == "?":
        screen.state = AppState.HELP
        return True
    
    if key == ' ':
        displayable_windows = [AppState.JOURNAL, AppState.ARCHIVE]
        if screen.state in displayable_windows:
            state_index = displayable_windows.index(screen.state)
            screen.state = displayable_windows[(state_index + 1) % len(displayable_windows)]
            return True

    if not key.isdigit():
        return False

    try:
        new_state = AppState(int(key))
        screen.state = new_state
        return True
    except ValueError:
        logging.error("Invalid new state")

    return False

@safe_run
def control_journal_screen(stdscr: curses.window, screen: Screen, user_tasks: Tasks):
    """Process user input on the journal screen"""
        
    # If we previously selected a task, now we perform the action:
    if screen.selection_mode:

        # Collapse/Expand
        if screen.key == 'c':
            number = input_integer(stdscr, MSG_TS_COLLAPSE)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_task_collapse(task)
        
        # Timer operations:
        if screen.key == 't':
            number = input_integer(stdscr, MSG_TM_ADD)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                if global_config.ONE_TIMER_AT_A_TIME:
                    user_tasks.pause_all_other_timers(task)
                user_tasks.add_timestamp_for_task(task)

        if screen.key == 'T':
            number = input_integer(stdscr, MSG_TM_RESET)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.reset_timer_for_task(task)

        # Add deadline:
        if screen.key == "f":
            number = input_integer(stdscr, MSG_TS_DEAD_ADD)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                year, month, day = input_date(stdscr, MSG_TS_DEAD_DATE)
                if screen.is_valid_date(year, month, day):
                    user_tasks.change_deadline(task, year, month, day)

        # Remove deadline:
        if screen.key == "F":
            number = input_integer(stdscr, MSG_TS_DEAD_DEL)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.change_deadline(task, 0, 0, 0)

        # Change the importance:
        if screen.key == 'i':
            number = input_integer(stdscr, MSG_TS_IMPORTANCE)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                new_importance = input_importance(stdscr)
                if new_importance is not None:
                    user_tasks.change_item_importance(task, new_importance)
        
        # Change the status:
        if screen.key == 's':
            number = input_integer(stdscr, MSG_TS_STATUS)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                new_status = input_status(stdscr)
                if new_status is not None:
                    user_tasks.change_item_status(task, new_status)
        
        if screen.key in ['d', 'v']:
            number = input_integer(stdscr, MSG_TS_DONE)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.change_item_status(task, Status.DONE)

        # Toggle task privacy:
        if screen.key == '.':
            number = input_integer(stdscr, MSG_TS_PRIVACY)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_privacy(task)

        # Modify the task:
        if screen.key in ['x']:
            number = input_integer(stdscr, MSG_TS_DEL)
            if number is not None and user_tasks.is_valid_number(number):
                task: Task = user_tasks.viewed_ordered_tasks[number]
                if task.children:
                    delete_children_as_well = ask_confirmation(stdscr, "Delete all children too?", True)
                else:
                    delete_children_as_well = False
                user_tasks.delete_task(task.item_id, delete_children_as_well)

        if screen.key == 'm':
            number_from = input_integer(stdscr, MSG_TS_MOVE)
            if number_from is not None and user_tasks.is_valid_number(number_from):
                number_to = input_integer(stdscr, MSG_TS_MOVE_TO)

                if number_to is not None and (user_tasks.is_valid_number(number_to) or number_to == -1):
                    src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                    if number_to == -1:
                        move_dest_task = user_tasks.root_task
                    else:
                        move_dest_task = user_tasks.viewed_ordered_tasks[number_to]

                    user_tasks.move_task(src_task, move_dest_task)

        if screen.key == 'r':
            number = input_integer(stdscr, MSG_TS_EDIT)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]

                new_name = input_string(stdscr, MSG_TS_RENAME_TASK,
                                        placeholder=MSG_TS_INPUT_TASK,
                                        default=task.name, autocomplete=global_config.icon_completer)
                if new_name:
                    user_tasks.rename_task(task, new_name)

        # Exchange operation
        if screen.key == 'e':
            number_from = input_integer(stdscr, MSG_TS_MOVE)
            if number_from is not None and user_tasks.is_valid_number(number_from):
                number_to = input_integer(stdscr, MSG_TS_MOVE_TO)

                if number_to is not None and user_tasks.is_valid_number(number_to):
                    src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                    swap_dest_task: Task = user_tasks.viewed_ordered_tasks[number_to]
                    user_tasks.swap_task(src_task, swap_dest_task)

        if screen.key == 'A':
            task_number: int|None = input_integer(stdscr, MSG_TS_SUB)
            if task_number is not None and user_tasks.is_valid_number(task_number):
                task_name = input_string(stdscr, MSG_TS_TITLE, placeholder=MSG_TS_INPUT_TASK, autocomplete=global_config.icon_completer)
                if task_name:
                    parent_task: Task = user_tasks.viewed_ordered_tasks[task_number]
                    user_tasks.add_subtask(task_name, parent_task)

        screen.selection_mode = False

    # Otherwise, we check for user input:
    else:
        if not screen.delayed_action:
            # Wait for user to press a key:
            screen.key = stdscr.getkey()
            
            if handle_screen_transfer_keys(stdscr, screen, screen.key):
                return

        # If we need to select a task, change to selection mode:
        selection_keys = ['t', 'T', 'v', 'u', 'i', 's', 'd', 'x', 'e', 'r', 'c', 'A', 'm', '.', 'f', 'F']
        if screen.key in selection_keys and user_tasks.viewed_ordered_tasks:
            screen.selection_mode = True

        # Add single task:
        if screen.key == "a":
            # TODO: Lower the screen offset if we're close to the edge
            if screen.delayed_action:
                # We delayed the action to move the offset
                screen.delayed_action = False

            amount_of_elements_on_screen = len(user_tasks.viewed_ordered_tasks[screen.offset:])
            if amount_of_elements_on_screen >= screen.y_max - HEADER_FIELD_COUNT - 1:
                # This means that we have more elements on the screen and we are at the edge
                amount_of_elements_on_screen = 5
                screen.offset = len(user_tasks.viewed_ordered_tasks) - amount_of_elements_on_screen
                screen.refresh_now = True
                screen.delayed_action = True
                return

            task_name = input_string(stdscr, MSG_TS_NEW_TASK, placeholder=MSG_TS_INPUT_TASK, autocomplete=global_config.icon_completer)
            if task_name:
                task_id = user_tasks.generate_id()
                user_tasks.add_item(Task(task_id, task_name, Status.NOT_STARTED, [], False, parent_id=0))

        # Bulk operations:
        if screen.key in ["X"]:
            confirmed = ask_confirmation(stdscr, MSG_TS_DEL_ALL, global_config.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.delete_all_items()

        if screen.key in ["KEY_DOWN"]:
            screen.change_offset_forwards(step_count=1)
        elif screen.key in ["KEY_UP"]:
            screen.change_offset_backwards(step_count=1)
        elif screen.key in ["KEY_PPAGE"]:
            screen.change_offset_backwards(step_count=6)
        elif screen.key in ["KEY_NPAGE"]:
            screen.change_offset_forwards(step_count=6)

        # Reload:
        if screen.key in ["Q"]:
            screen.reload_data = True
            screen.refresh_now = True

        handle_screen_transfer_keys(stdscr, screen, screen.key)

@safe_run
def control_help_screen(stdscr, screen):
    """Process user input on the help screen"""
    # Getting user's input:
    screen.key = stdscr.getkey()

    # Handle vim-style exit on "ZZ" and "ZQ":
    if vim_style_exit(stdscr, screen):
        confirmed = ask_confirmation(stdscr, MSG_EXIT, global_config.ASK_CONFIRMATION_TO_QUIT)
        screen.state = AppState.EXIT if confirmed else screen.state

    # Handle keys to exit the help screen:
    if screen.key in [" ", "?", "q", "^[", "\x7f"]:
        screen.state = AppState.JOURNAL

@safe_run
def control_welcome_screen(stdscr, screen):
    """Process user input on the welcome screen"""
    # Getting user's input:
    screen.key = stdscr.getkey()

    # Handle key to call help screen:
    if screen.key in ["?"]:
        screen.state = AppState.HELP

    # Otherwise, just start the program:
    else:
        screen.state = AppState.JOURNAL

@safe_run
def control_archive_screen(stdscr: curses.window, screen: Screen, user_tasks: Tasks):
    """Process user input on the welcome screen"""
    
    if screen.selection_mode:
        screen.selection_mode = False

        if screen.key == "x":
            number = input_integer(stdscr, MSG_TS_RES)
            if number is not None and user_tasks.is_valid_archive_number(number):
                task: Task = user_tasks.viewed_archived_ordered_tasks[number]
                if task.children:
                    restore_children_as_well = ask_confirmation(stdscr, "Restore all children too?", True)
                else:
                    restore_children_as_well = False
                
                user_tasks.restore_item_from_archive_with_children(task, restore_children_as_well)
    else:
        # Getting user's input:
        screen.key = stdscr.getkey()

        if screen.key in ["x"]:
            screen.selection_mode = True

        handle_screen_transfer_keys(stdscr, screen, screen.key)

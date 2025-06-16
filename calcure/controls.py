"""This module contains functions that react to user input on each screen"""

import curses
import importlib

# Modules:
from calcure.data import *
from calcure.dialogues import *
from calcure.configuration import Config
from calcure.screen import Screen

cf = Config()

# Language:
if cf.LANG == "fr":
    from calcure.translations.fr import *
elif cf.LANG == "ru":
    from calcure.translations.ru import *
elif cf.LANG == "it":
    from calcure.translations.it import *
elif cf.LANG == "br":
    from calcure.translations.br import *
elif cf.LANG == "tr":
    from calcure.translations.tr import *
elif cf.LANG == "zh":
    from calcure.translations.zh import *
elif cf.LANG == "tw":
    from calcure.translations.tw import *
elif cf.LANG == "sk":
    from calcure.translations.sk import *
else:
    from calcure.translations.en import *


def safe_run(func):
    """Decorator preventing crashes on keyboard interruption and no input"""

    def inner(stdscr, screen, *args, **kwargs):
        try:
            func(stdscr, screen, *args, **kwargs)

        # Handle keyboard interruption with ctrl+c:
        except KeyboardInterrupt:
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state

        # Prevent crash if no input:
        except curses.error:
            pass
    return inner


@safe_run
def control_monthly_screen(stdscr, screen, user_events, importer):
    """Handle user input on the monthly screen"""

    # If we previously entered the selection mode, now we perform the action:
    if screen.selection_mode:
        screen.selection_mode = False

        # Change event status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_HIGH)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.IMPORTANT)
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_LOW)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.UNIMPORTANT)
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_RESET)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.NORMAL)
        if screen.key == 'd':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DONE)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.DONE)

        # Toggle event privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_PRIVACY)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_privacy(event_id)

        # Delete event:
        if screen.key == 'x':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DEL)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.delete_item(event_id)

        # Rename event:
        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REN)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                new_name = input_string(stdscr, screen.y_max-2, 0, MSG_NEW_TITLE, screen.x_max-len(MSG_NEW_TITLE)-2)
                user_events.rename_item(event_id, new_name)

        # Move event:
        if screen.key in ['m', 'M']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_MV)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                if screen.key == 'm':
                    year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_MV_TO)
                    if screen.is_valid_date(year, month, day):
                        user_events.change_date(event_id, year, month, day)

                if screen.key == 'M':
                    question = f'{MSG_EVENT_MV_TO_D} {screen.year}/{screen.month}/'
                    day = input_day(stdscr, screen.y_max-2, 0, question)
                    if screen.is_valid_day(day):
                        user_events.change_day(event_id, day)

    # Otherwise, we check for user input:
    else:
        # Wait for user to press a key:
        screen.key = stdscr.getkey()

        # If we need to select an event, change to selection mode:
        selection_keys = ['h', 'l', 'u', 'i', 'd', 'x', 'e', 'r', 'c', 'm', 'M', '.']
        if screen.key in selection_keys and user_events.filter_events_that_month(screen).items:
            screen.selection_mode = True

        # Navigation:
        if screen.key in ["n", "j", "KEY_DOWN", "KEY_RIGHT"]:
            screen.next_month()
        if screen.key in ["p", "k", "KEY_UP", "KEY_LEFT"]:
            screen.previous_month()
        if screen.key in ["KEY_HOME", "R"]:
            screen.reset_to_today()

        # Handle "g" and "G" as go to selected day:
        if screen.key == "g":
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_GOTO)
            if screen.is_valid_date(year, month, day):
                screen.day = day
                screen.month = month
                screen.year = year
                screen.calendar_state = CalState.DAILY

        if screen.key == "G":
            clear_line(stdscr, screen.y_max-2, 0)
            question = f"{MSG_GOTO_D} {screen.year}/{screen.month}/"
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_date(screen.year, screen.month, day):
                screen.day = day
                screen.calendar_state = CalState.DAILY

        # Change the view to daily:
        if screen.key == "v":
            screen.day = 1
            screen.calendar_state = CalState.DAILY

        # Add single event:
        if screen.key == "a":
            question = f'{MSG_EVENT_DATE} {screen.year}/{screen.month}/'
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_day(day):
                clear_line(stdscr, screen.y_max-2)
                name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
                event_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                user_events.add_item(UserEvent(event_id, screen.year, screen.month, day, name, 1, Frequency.ONCE, Status.NORMAL, False))

        # Add a recurring event:
        if screen.key == "A":
            question = f'{MSG_EVENT_DATE}{screen.year}/{screen.month}/'
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_day(day):
                clear_line(stdscr, screen.y_max-2)
                name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
                item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                reps = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REP)
                freq = input_frequency(stdscr, screen.y_max-2, 0, MSG_EVENT_FR)
                if reps is not None and freq is not None:
                    reps = 1 if reps == 0 else reps
                    user_events.add_item(UserEvent(item_id, screen.year, screen.month, day, name, reps+1, freq, Status.NORMAL, False))

        # Reload:
        if screen.key in ["Q"]:
            screen.reload_data = True
            screen.refresh_now = True

        # Imports:
        if screen.key == "C":
            confirmed = ask_confirmation(stdscr, MSG_EVENT_IMP, cf.ASK_CONFIRMATIONS)
            if confirmed:
                importer.import_events_from_calcurse()
                screen.refresh_now = True

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        if screen.key in [" ", "KEY_BTAB"]:
            screen.state = AppState.JOURNAL
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key in ["/"]:
            screen.split = not screen.split
            screen.refresh_now = True


@safe_run
def control_daily_screen(stdscr, screen, user_events, importer):
    """Handle user input on the daily screen"""
    # If we previously entered the selection mode, now we perform the action:
    if screen.selection_mode:
        screen.selection_mode = False

        # Change event status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_HIGH)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.IMPORTANT)
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_LOW)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.UNIMPORTANT)
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_RESET)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.NORMAL)
        if screen.key == 'd':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DONE)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.DONE)

        # Toggle event privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_PRIVACY)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_privacy(event_id)

        # Delete event:
        if screen.key in ['x']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DEL)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.delete_item(item_id)

        # Rename event:
        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REN)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                new_name = input_string(stdscr, screen.y_max-2, 0, MSG_NEW_TITLE, screen.x_max-len(MSG_NEW_TITLE)-2)
                user_events.rename_item(item_id, new_name)

        # Move event:
        if screen.key in ['m', 'M']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_MV)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                if screen.key == 'm':
                    year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_MV_TO)
                    if screen.is_valid_date(year, month, day):
                        user_events.change_date(event_id, year, month, day)

                if screen.key == 'M':
                    question = f'{MSG_EVENT_MV_TO_D}{screen.year}/{screen.month}/'
                    day = input_day(stdscr, screen.y_max-2, 0, question)
                    if screen.is_valid_day(day):
                        user_events.change_day(event_id, day)

    # Otherwise, we check for user input:
    else:
        # Wait for user to press a key:
        screen.key = stdscr.getkey()

        # If we need to select an event, change to selection mode:
        selection_keys = ['h', 'l', 'u', 'i', 'd', 'x', 'e', 'r', 'c', 'm', 'M', '.']
        if screen.key in selection_keys and user_events.filter_events_that_day(screen).items:
            screen.selection_mode = True

        # Navigation:
        if screen.key in ["n", "j", "KEY_UP", "KEY_RIGHT"]:
            screen.next_day()
        if screen.key in ["p", "k", "KEY_DOWN", "KEY_LEFT"]:
            screen.previous_day()
        if screen.key in ["KEY_HOME", "R"]:
            screen.reset_to_today()

        # Add single event:
        if screen.key == "a":
            name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
            item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
            user_events.add_item(UserEvent(item_id, screen.year, screen.month, screen.day, name, 1, Frequency.ONCE, Status.NORMAL, False))

        # Add a recurring event:
        if screen.key == "A":
            name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
            item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
            reps = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REP)
            freq = input_frequency(stdscr, screen.y_max-2, 0, MSG_EVENT_FR)
            if reps is not None and freq is not None:
                reps = 1 if reps == 0 else reps
                user_events.add_item(UserEvent(item_id, screen.year, screen.month, screen.day, name, reps+1, freq, Status.NORMAL, False))

        # Import from calcurse:
        if screen.key == "C":
            confirmed = ask_confirmation(stdscr, MSG_EVENT_IMP, cf.ASK_CONFIRMATIONS)
            if confirmed:
                importer.import_events_from_calcurse()

        # Handle "g" and "G" as go to selected (prefilled) day:
        if screen.key == "g":
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_GOTO)
            if screen.is_valid_date(year, month, day):
                screen.day = day
                screen.month = month
                screen.year = year
                screen.calendar_state = CalState.DAILY

        if screen.key == "G":
            clear_line(stdscr, screen.y_max-2, 0)
            question = f"{MSG_GOTO_D} {screen.year}/{screen.month}/"
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_date(screen.year, screen.month, day):
                screen.day = day
                screen.calendar_state = CalState.DAILY

        # Reload:
        if screen.key == "Q":
            screen.reload_data = True
            screen.refresh_now = True

        # Change the view to monthly:
        if screen.key == "v":
            screen.calendar_state = CalState.MONTHLY

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        if screen.key in [" ", "KEY_BTAB"]:
            screen.state = AppState.JOURNAL
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key in ["/"]:
            screen.split = not screen.split
            screen.refresh_now = True

HEADER_FIELD_COUNT = 2

@safe_run
def control_journal_screen(stdscr, screen: Screen, user_tasks: Tasks, importer):
    """Process user input on the journal screen"""
        
    # If we previously selected a task, now we perform the action:
    if screen.selection_mode:

        # Collapse/Expand
        if screen.key == 'c':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TM_ADD)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_task_collapse(task)
        
        # Timer operations:
        if screen.key == 't':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TM_ADD)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                if cf.ONE_TIMER_AT_A_TIME:
                    user_tasks.pause_all_other_timers(task)
                user_tasks.add_timestamp_for_task(task)

        if screen.key == 'T':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TM_RESET)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.reset_timer_for_task(task)

        # Add deadline:
        if screen.key == "f":
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_ADD)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                clear_line(stdscr, screen.y_max-2, 0)
                year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_DATE)
                if screen.is_valid_date(year, month, day):
                    user_tasks.change_deadline(task, year, month, day)

        # Remove deadline:
        if screen.key == "F":
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_DEL)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.change_deadline(task, 0, 0, 0)

        # Change the status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_HIGH)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_status(task, Status.IMPORTANT)
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_LOW)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_status(task, Status.UNIMPORTANT)
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_RES)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_status(task, Status.NORMAL)
        if screen.key in ['d', 'v']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DONE)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_status(task, Status.DONE)

        # Toggle task privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_PRIVACY)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]
                user_tasks.toggle_item_privacy(task)

        # Modify the task:
        if screen.key in ['x']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEL)
            if number is not None and user_tasks.is_valid_number(number):
                task: Task = user_tasks.viewed_ordered_tasks[number]
                if task.children:
                    delete_children_as_well = ask_confirmation(stdscr, "Delete all children too? (y/n)", True)
                else:
                    delete_children_as_well = False
                user_tasks.delete_task(task.item_id, delete_children_as_well)

        if screen.key == 'm':
            number_from = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE)
            if number_from is not None and user_tasks.is_valid_number(number_from):
                clear_line(stdscr, screen.y_max-2)
                number_to = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE_TO)

                if number_to is not None and user_tasks.is_valid_number(number_to):
                    src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                    dest_task: Task = user_tasks.viewed_ordered_tasks[number_to]

                    user_tasks.move_task(src_task, dest_task)

        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_EDIT)
            if number is not None and user_tasks.is_valid_number(number):
                task = user_tasks.viewed_ordered_tasks[number]

                number_relative_to_offset = number + 2 - screen.offset 
                clear_line(stdscr, number_relative_to_offset, screen.x_min)
                new_name = input_string(stdscr, number_relative_to_offset, screen.x_min + 4 + user_tasks.get_indent_count(task), cf.TODO_ICON+' ', screen.x_max-4)
                if new_name:
                    user_tasks.rename_task(task, new_name)

        # Swap operation
        if screen.key == 's':
            number_from = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE)
            if number_from is not None and user_tasks.is_valid_number(number_from):
                clear_line(stdscr, screen.y_max-2)
                number_to = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE_TO)

                if number_to is not None and user_tasks.is_valid_number(number_to):
                    src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                    dest_task: Task = user_tasks.viewed_ordered_tasks[number_to]
                    user_tasks.swap_task(src_task, dest_task)

        if screen.key == 'A':
            task_number: int|None = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_SUB)
            if task_number is not None and user_tasks.is_valid_number(task_number):
                clear_line(stdscr, screen.y_max-2, 0)
                task_name = input_string(stdscr, screen.y_max-2, 0, MSG_TS_TITLE, screen.x_max-len(MSG_TS_TITLE)-2)
                if task_name:
                    parent_task: Task = user_tasks.viewed_ordered_tasks[task_number]
                    user_tasks.add_subtask(task_name, parent_task)

        screen.selection_mode = False

    # Otherwise, we check for user input:
    else:
        if not screen.delayed_action:
            # Wait for user to press a key:
            screen.key = stdscr.getkey()

        # If we need to select a task, change to selection mode:
        selection_keys = ['t', 'T', 'h', 'l', 'v', 'u', 'i', 's', 'd', 'x', 'e', 'r', 'c', 'A', 'm', '.', 'f', 'F']
        if screen.key in selection_keys and user_tasks.viewed_ordered_tasks:
            screen.selection_mode = True

        # Add single task:
        if screen.key == "a":
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

            y_offset = amount_of_elements_on_screen + HEADER_FIELD_COUNT
            clear_line(stdscr, y_offset, screen.x_min)
            task_name = input_string(stdscr, y_offset, screen.x_min + 4, cf.TODO_ICON+' ', screen.x_max - 4)
            if task_name:
                task_id = user_tasks.generate_id()
                user_tasks.add_item(Task(task_id, task_name, Status.NORMAL, Timer([]), False, parent_id=0))

        # Bulk operations:
        if screen.key in ["X"]:
            confirmed = ask_confirmation(stdscr, MSG_TS_DEL_ALL, cf.ASK_CONFIRMATIONS)
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

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        if screen.key in [" ", "KEY_BTAB"]:
            screen.state = AppState.CALENDAR
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key in ["/"]:
            screen.split = not screen.split
            screen.refresh_now = True


@safe_run
def control_help_screen(stdscr, screen):
    """Process user input on the help screen"""
    # Getting user's input:
    screen.key = stdscr.getkey()

    # Handle vim-style exit on "ZZ" and "ZQ":
    if vim_style_exit(stdscr, screen):
        confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
        screen.state = AppState.EXIT if confirmed else screen.state

    # Handle keys to exit the help screen:
    if screen.key in [" ", "?", "q", "^[", "\x7f"]:
        screen.state = AppState.CALENDAR


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
        screen.state = AppState.CALENDAR

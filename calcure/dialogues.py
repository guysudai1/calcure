""" Module that controls interactions with the user, like questions and confirmations"""

import curses
from datetime import datetime
from email.errors import InvalidMultipartContentTransferEncodingDefect
import logging
import sys

from prompt_toolkit.shortcuts import confirm

from calcure.colors import Color
from calcure.singletons import global_config
from calcure.consts import Filters, Importance, Status

import prompt_toolkit

from calcure.screen import Screen
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.formatted_text import FormattedText

from calcure.translations.en import MSG_TS_FILTER, MSG_TS_FILTER_EXTRA_INFO, MSG_TS_FILTER_NAME


def safe_run(func):
    """Decorator preventing crashes on keyboard interruption and no input"""

    def inner(stdscr, screen, *args, **kwargs):
        try:
            func(stdscr, screen, *args, **kwargs)

        # Handle keyboard interruption with ctrl+c:
        except KeyboardInterrupt:
            pass

        # Prevent crash if no input:
        except curses.error:
            pass
    return inner



def clear_line(stdscr, y, x=0):
    """Clear a line from any text"""
    _, x_max = stdscr.getmaxyx()
    stdscr.addstr(y, x, " " * (x_max - x - 1), curses.color_pair(Color.EMPTY.value))



def input_string(stdscr: curses.window, question, default="", placeholder: str|None=None, autocomplete: Completer|None=None, **kwargs):
    """Ask user to input something and return it as a string"""
    move_cursor_to_input_position(stdscr)

    if placeholder is not None:
        placeholder_formatted = FormattedText([
            ('#787878', placeholder),
        ])
    else:
        placeholder_formatted = None 
    
    answer = prompt_toolkit.prompt(message=question, default=default, reserve_space_for_menu=amount_of_rows_prompt_toolkit_takes, placeholder=placeholder_formatted, completer=autocomplete, **kwargs)
    stdscr.refresh()
    stdscr.keypad(True)  # This is used for us to be able to use KEY_* again
    return answer

def input_path(stdscr: curses.window, question, default="", placeholder: str|None=None, **kwargs):
    """Ask user to input something and return it as a string"""
    kwargs.pop("completer", None)  # Remove completer if we have one
    return input_string(stdscr, question, default, placeholder, PathCompleter(expanduser=True))

def input_integer(stdscr, question, is_index=True, display_error=True, **kwargs):
    """Ask user for an integer number and check if it is an integer"""
    number = input_string(stdscr, question, **kwargs)
    try:
        number = int(number)
        if is_index:
            number -= 1
    except (ValueError, KeyboardInterrupt):
        if display_error:
            logging.warning("Incorrect number input.")
        return None
    return number

def input_filter_content(stdscr, filter_chosen: Filters):
    match filter_chosen:
        case Filters.NAME | Filters.EXTRA_INFO:
            if filter_chosen == Filters.NAME:
                msg = MSG_TS_FILTER_NAME
            elif filter_chosen == Filters.EXTRA_INFO:
                msg = MSG_TS_FILTER_EXTRA_INFO
            else:
                raise Exception("Invalid filter chosen")
            filter_content = input_string(stdscr, msg)
        case Filters.STATUS:
            filter_content = input_status(stdscr)
        case Filters.IMPORTANCE:
            filter_content = input_importance(stdscr)
        case _:
            raise Exception("Invalid filter chosen")

    return filter_content

def input_filter_field(stdscr, question, **kwargs):
    question = []
    for filter_enum in Filters:
        question.append(f"{filter_enum.value}={filter_enum.name}")
    question_str = ", ".join(question)

    kwargs["bottom_toolbar"] = question_str
    display_error = kwargs.pop("display_error", True)
    number = input_integer(stdscr, MSG_TS_FILTER, is_index=False, display_error=display_error, **kwargs)
    if number is None:
        return None

    try:
        filter_chosen = Filters(number)
    except ValueError:
        return None
    
    return filter_chosen

def input_status(stdscr):
    """Ask user for an integer representing a task status"""
    question = []
    for status_enum in Status:
        question.append(f"{status_enum.value}={status_enum.name}")
    question_str = ", ".join(question)
    question_str += " : " 
    number = input_integer(stdscr, "New task status: ",  is_index=False, bottom_toolbar=question_str)
    try:
        return Status(number)
    except ValueError:
        logging.error("Invalid status number entered")
        return None

def input_importance(stdscr):
    """Ask user for an integer representing task importance"""
    bottom_toolbar = "Optional - can be deferred, Low - nice to have, Medium - far future, High - near future, Critical - ASAP" 

    question_str = "Undecided (0), Optional (1-2), Low (3-4), Medium (5-6), High (7-8), Critical (9-10): " 
    number = input_integer(stdscr, question_str, is_index=False, bottom_toolbar=bottom_toolbar)
    try:
        return Importance(number)
    except ValueError:
        logging.error("Invalid importance number entered")
        return None

def input_date(stdscr, prompt_string):
    """Ask user to input date in YYYY/MM/DD format and check if it was a valid entry"""
    date_unformatted = input_string(stdscr, prompt_string)
    try:
        return datetime.strptime(date_unformatted, r'%Y/%m/%d').date()
    except (ValueError, IndexError, KeyboardInterrupt):
        logging.warning("Incorrect date input.")
        return None

amount_of_rows_prompt_toolkit_takes = 4

def move_cursor_to_x_y(x: int, y: int):
    sys.stdout.write(f'\033[{x};{y}H')
    sys.stdout.flush()

def move_cursor_to_input_position(stdscr: curses.window):
    stdscr.refresh()

    # Move the cursor to the last lines of the terminal and to the beginning of the line
    rows, _ = stdscr.getmaxyx()
    extra_space = 2 # for prettiness

    # Go to (max_y - 10, 0). This moves the cursor 10 lines before the end of the terminal
    #   and to the first character
    move_cursor_to_x_y(rows - amount_of_rows_prompt_toolkit_takes - extra_space, 0)

def ask_confirmation(stdscr: curses.window, question):
    """Ask user confirmation for an action"""

    move_cursor_to_input_position(stdscr)
    return confirm(message=question)


def vim_style_exit(stdscr, screen):
    """Handle vim style key combinations like ZZ and ZQ for exit"""
    if screen.key == "Z":
        try:
            screen.key = stdscr.getkey()
            return (screen.key in ["Z", "Q"])
        except KeyboardInterrupt:
            return True
    else:
        return False

""" Module that controls interactions with the user, like questions and confirmations"""

import curses
from email.errors import InvalidMultipartContentTransferEncodingDefect
import logging
import sys

from calcure.colors import Color
from calcure.singletons import global_config
from calcure.consts import Importance, Status

import prompt_toolkit

from calcure.screen import Screen
from prompt_toolkit.completion import Completer, Completion

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



def display_question(stdscr, y, x, question, color):
    """Display the line of text respecting the styling and available space"""
    y_max, x_max = stdscr.getmaxyx()
    if y >= y_max or x >= x_max:
        return
    question = question[:(x_max - x - 1)]
    stdscr.addstr(y, x, question, curses.color_pair(color.value))


def clear_line(stdscr, y, x=0):
    """Clear a line from any text"""
    _, x_max = stdscr.getmaxyx()
    stdscr.addstr(y, x, " " * (x_max - x - 1), curses.color_pair(Color.EMPTY.value))


def input_field(stdscr, y, x, field_length):
    """Input field that gets characters entered by user"""
    curses.curs_set(1)
    input_str = ""
    cursor_pos = 0

    curses.cbreak()
    stdscr.timeout(-1)
    stdscr.nodelay(False)
    stdscr.notimeout(True)

    while True:
        stdscr.move(y, x + cursor_pos)
        key = stdscr.get_wch()

        # Regular Unicode characters:
        if isinstance(key, str):
            if ord(key) == 27: # Esc
                return ""
            elif ord(key) in (10, 13): # Enter
                return input_str
            elif ord(key) == 127 and cursor_pos > 0: # Backspace
                input_str = input_str[:cursor_pos-1] + input_str[cursor_pos:]
                cursor_pos -= 1
            elif cursor_pos < field_length: # Other characters:
                input_str = input_str[:cursor_pos] + chr(ord(key)) + input_str[cursor_pos:]
                cursor_pos += 1
            else:
                pass

        # Various keys:
        else:
            if key == curses.KEY_ENTER:
                return input_str
            elif key == curses.KEY_BACKSPACE and cursor_pos > 0:
                input_str = input_str[:cursor_pos-1] + input_str[cursor_pos:]
                cursor_pos -= 1
            elif key == curses.KEY_LEFT and cursor_pos > 0:
                cursor_pos -= 1
            elif key == curses.KEY_RIGHT and cursor_pos < len(input_str):
                cursor_pos += 1
            else:
                pass


        # Redraw input field:
        stdscr.addstr(y, x, input_str + " ")
        stdscr.refresh()

from prompt_toolkit.formatted_text import FormattedText

def input_string(stdscr: curses.window, y, x, question, default="", placeholder: str|None=None, autocomplete: Completer|None=None):
    """Ask user to input something and return it as a string"""
    stdscr.refresh()

    # Move the cursor to the last lines of the terminal and to the beginning of the line
    rows, _ = stdscr.getmaxyx()
    amount_of_rows_prompt_toolkit_takes = 4
    extra_space = 2 # for prettiness

    # Go to (max_y - 10, 0). This moves the cursor 10 lines before the end of the terminal
    #   and to the first character
    sys.stdout.write(f'\033[{rows - amount_of_rows_prompt_toolkit_takes - extra_space};0H')
    sys.stdout.flush()

    if placeholder is not None:
        placeholder_formatted = FormattedText([
            ('#787878', placeholder),
        ])
    else:
        placeholder_formatted = None 
    
    answer = prompt_toolkit.prompt(message=question, default=default, reserve_space_for_menu=amount_of_rows_prompt_toolkit_takes, placeholder=placeholder_formatted, completer=autocomplete)
    stdscr.refresh()
    stdscr.keypad(True)  # This is used for us to be able to use KEY_* again
    return answer


def input_integer(stdscr, y, x, question, is_index=True):
    """Ask user for an integer number and check if it is an integer"""
    number = input_string(stdscr, y, x, question)
    try:
        number = int(number)
        if is_index:
            number -= 1
    except (ValueError, KeyboardInterrupt):
        logging.warning("Incorrect number input.")
        return None
    return number

def input_status(stdscr, y, x):
    """Ask user for an integer representing a task status"""
    question = []
    for status_enum in Status:
        question.append(f"{status_enum.value}={status_enum}")
    question_str = ", ".join(question)
    question_str += " : " 
    number = input_integer(stdscr, y, x, question_str, is_index=False)
    try:
        return Status(number)
    except ValueError:
        logging.error("Invalid status number entered")
        return None

def input_importance(stdscr, y, x):
    """Ask user for an integer representing task importance"""
    question_str = "levels: Optional - can be deferred, Low - nice to have, Medium - far future, High - near future, Critical - ASAP" 
    display_question(stdscr, y - 1, x, question_str, Color.PROMPTS)

    question_str = "Undecided (0), Optional (1-2), Low (3-4), Medium (5-6), High (7-8), Critical (9-10): " 
    number = input_integer(stdscr, y, x, question_str, is_index=False)
    try:
        return Importance(number)
    except ValueError:
        logging.error("Invalid importance number entered")
        return None

def input_date(stdscr, y, x, prompt_string):
    """Ask user to input date in YYYY/MM/DD format and check if it was a valid entry"""
    date_unformatted = input_string(stdscr, y, x, prompt_string)
    try:
        year = int(date_unformatted.split("/")[0])
        month = int(date_unformatted.split("/")[1])
        day = int(date_unformatted.split("/")[2])
        return year, month, day
    except (ValueError, IndexError, KeyboardInterrupt):
        logging.warning("Incorrect date input.")
        return None, None, None



def ask_confirmation(stdscr: curses.window, question, confirmations_enabled):
    """Ask user confirmation for an action"""
    if not confirmations_enabled:
        return True
    y_max, _ = stdscr.getmaxyx()
    curses.halfdelay(255)

    clear_line(stdscr, y_max - 2)
    display_question(stdscr, y_max - 2, 0, question, Color.CONFIRMATIONS)
    key = stdscr.getkey()
    confirmed = (key == "y")
    return confirmed


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

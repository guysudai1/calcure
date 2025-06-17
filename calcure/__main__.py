#!/usr/bin/env python

"""This is the main module that contains views and the main logic"""

import curses
import time
import getopt
import sys
import importlib
import threading

from calcure.calendars import Calendar
from calcure.errors import Error
from calcure.configuration import Config
from calcure.dialogues import clear_line
from calcure.screen import Screen
from calcure.savers import TaskSaverCSV
from calcure.colors import Color, initialize_colors
from calcure.loaders import *
from calcure.data import *
from calcure.controls import *


# Initialise config:
cf = Config()
error = Error(cf.LOG_FILE)

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


__version__ = "3.2.1"


class View:
    """Parent class of a view that displays things at certain coordinates"""

    def __init__(self, stdscr, y, x):
        self.stdscr = stdscr
        self.y = y
        self.x = x

    def fill_background(self):
        """Fill the screen background with background color"""
        y_max, x_max = self.stdscr.getmaxyx()
        for index in range(y_max - 1):
            self.stdscr.addstr(index, 0, " " * x_max, curses.color_pair(Color.EMPTY.value))

    def display_line(self, y, x, text, color, bold=False, underlined=False):
        """Display the line of text respecting the slyling and available space"""

        # Make sure that we display inside the screen:
        y_max, x_max = self.stdscr.getmaxyx()
        if y >= y_max or x >= x_max:
            return
        # Cut the text if it does not fit the screen:
        real_text = text.replace('\u0336', "")
        number_of_characters = len(real_text)
        available_space = x_max - x
        number_of_special = text.count('\u0336')
        if number_of_characters > available_space:
            coefficient = 2 if number_of_special > 0 else 1
            text = f"{text[:(available_space - 1)*coefficient]}"

        try:
            if bold and underlined:
                self.stdscr.addstr(y, x, text, curses.color_pair(color.value) | curses.A_BOLD | curses.A_UNDERLINE)
            elif bold and not underlined:
                self.stdscr.addstr(y, x, text, curses.color_pair(color.value) | curses.A_BOLD)
            elif underlined and not bold:
                self.stdscr.addstr(y, x, text, curses.color_pair(color.value) | curses.A_UNDERLINE)
            else:
                self.stdscr.addstr(y, x, text, curses.color_pair(color.value))
        except curses.error: # Fix for occasional error with large zoom (reason is unclear)
            return


class TaskView(View):
    """Display a single task"""

    def __init__(self, stdscr, y, x, task: Task, screen, indent: int):
        super().__init__(stdscr, y, x)
        self.task = task
        self.screen = screen
        self.task_indent = indent

    @property
    def color(self):
        """Select the color depending on the status"""
        if self.task.status == Status.DONE:
            return Color.DONE
        if self.task.status == Status.IMPORTANT:
            return Color.IMPORTANT
        if self.task.status == Status.UNIMPORTANT:
            return Color.UNIMPORTANT
        return Color.TODO

    @property
    def icon(self):
        """Select the icon for the task"""
        icon = cf.TODO_ICON
        if cf.DISPLAY_ICONS:
            for keyword in cf.ICONS:
                if keyword in self.task.name.lower():
                    icon = cf.ICONS[keyword]

        if self.task.status == Status.DONE:
            icon = cf.DONE_ICON
        if self.task.status == Status.IMPORTANT:
            icon = cf.IMPORTANT_ICON
        return icon

    @property
    def info(self):
        """Icon and name of the task, which is decorated if needed"""
        name = self.task.name
        if self.screen.privacy or self.task.privacy:
            return f'{cf.TODO_ICON} {cf.PRIVACY_ICON * len(name)}'

        if self.task.status == Status.DONE and cf.STRIKETHROUGH_DONE:
            strike = "\u0336"
            info_str = f'{self.icon} {strike}{strike.join(name)}{strike}'
        else:
            info_str = f'{self.icon} {name}'

        if self.task.collapse:
            info_str += f" {cf.COLLAPSED_ICON}"

        return info_str

    def render(self):
        """Render a line with an icon, task, deadline, and timer"""
        self.display_line(self.y, self.x + self.task_indent + 4, self.info, self.color)

        deadline_indentation = self.screen.x_min + 6 + len(self.info) + self.task_indent
        deadline_view = TaskDeadlineView(self.stdscr, self.y, deadline_indentation, self.task)
        deadline_view.render()

        addition_indentation = (deadline_view.has_deadline)*(4 + len(deadline_view.info))
        timer_indentation = deadline_indentation + addition_indentation
        timer_view = TimerView(self.stdscr, self.y, timer_indentation, self.task.timer)
        timer_view.render()


class TaskDeadlineView(View):
    """Display deadline for a task"""

    def __init__(self, stdscr, y, x, task):
        super().__init__(stdscr, y, x)
        self.task = task
        self.color = Color.DEADLINES
        self.icon = cf.DEADLINE_ICON
        self.info = f"{self.task.year}/{self.task.month}/{self.task.day}"
        self.has_deadline = (self.task.year > 0)

    def render(self):
        """Render a line with the deadline date and icon"""
        if self.has_deadline:
            self.display_line(self.y, self.x, f"{self.icon} {self.info}", self.color)


class TimerView(View):
    """Display timer for a task"""

    def __init__(self, stdscr, y, x, timer):
        super().__init__(stdscr, y, x)
        self.timer = timer
        self.color = Color.TIMER if self.timer.is_counting else Color.TIMER_PAUSED

    @property
    def icon(self):
        """Return icon corresponding to timer state"""
        TIMER_RUNS_ICON = "⏵" if cf.DISPLAY_ICONS else "·"
        TIMER_PAUSED_ICON = "⏯︎" if cf.DISPLAY_ICONS else "·"
        return TIMER_RUNS_ICON if self.timer.is_counting else TIMER_PAUSED_ICON

    def render(self):
        """Render a line with a timer and icon"""
        if self.timer.is_started:
            self.display_line(self.y, self.x, f"{self.icon} {self.timer.passed_time}", self.color)


class JournalView(View):
    """Displays a list of all tasks"""

    def __init__(self, stdscr, y, x, user_tasks: Tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen


    def render(self):
        """Render the list of tasks"""
        if self.y == 0:
            self.y += 1

        all_tasks = self.user_tasks.viewed_ordered_tasks

        if not all_tasks and cf.SHOW_NOTHING_PLANNED:
            self.display_line(self.y, self.x, MSG_TS_NOTHING, Color.UNIMPORTANT)
        
        relevant_task_list = all_tasks[self.screen.offset:]
        self.display_line(self.y - 1, self.x, color=Color.TITLE, bold=True,
                          text=f"# Tasks displayed: {len(relevant_task_list)}/{len(all_tasks)}. Offset: {self.screen.offset}")
        for index, task in enumerate(relevant_task_list, start=self.screen.offset):
            task_view = TaskView(self.stdscr, self.y, self.x, task, self.screen, indent=self.user_tasks.get_indent_count(task))
            task_view.render()
            if self.screen.selection_mode and self.screen.state == AppState.JOURNAL:
                self.display_line(self.y, self.x, str(index + 1), Color.ACTIVE_PANE)
            self.y += 1

        self.y += 1
        # for index, task in enumerate(self.user_ics_tasks.items):
        #     task_view = TaskView(self.stdscr, self.y, self.x, task, self.screen)
        #     task_view.render()
        #     self.y += 1


class TitleView(View):
    """Show the title in the header"""

    def __init__(self, stdscr, y, x, title, screen):
        super().__init__(stdscr, y, x)
        self.title = title
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        if self.screen.is_active_pane and self.screen.split:
            self.display_line(0, self.screen.x_min, self.title, Color.ACTIVE_PANE, cf.BOLD_ACTIVE_PANE, cf.UNDERLINED_ACTIVE_PANE)
        else:
            self.display_line(0, self.screen.x_min, self.title, Color.CALENDAR_HEADER, cf.BOLD_TITLE, cf.UNDERLINED_TITLE)


class HeaderView(View):
    """Show the header that includes the time, and title"""

    def __init__(self, stdscr, y, x, title, screen):
        super().__init__(stdscr, y, x)
        self.title = title
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        _, x_max = self.stdscr.getmaxyx()

        # Show title:
        title_view = TitleView(self.stdscr, 0, self.screen.x_min, self.title, self.screen)
        title_view.render()

        if self.screen.currently_drawn == AppState.JOURNAL and self.screen.split:
            return

        # Show time:
        time_string = time.strftime("%H:%M", time.localtime())
        size_allows = len(time_string) < self.screen.x_max - len(self.title)
        if cf.SHOW_CURRENT_TIME and size_allows:
            self.display_line(0, (self.screen.x_max // 2 - 2), time_string, Color.TIME)


class FooterView(View):
    """Display the footer with keybinding"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        if not cf.SHOW_KEYBINDINGS: 
            return
        clear_line(self.stdscr, self.screen.y_max - 1)
        if self.screen.state == AppState.JOURNAL:
            hint = JOURNAL_HINT
            self.display_line(self.screen.y_max - 1, 0, hint, Color.HINTS)


class ErrorView(View):
    """Display the error messages"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen
        self.error = error


    def render(self):
        """Render this view on the screen"""
        if self.error.has_occurred:
            clear_line(self.stdscr, self.screen.y_max - 2)

            # Depending on error type, display different messages:
            if self.error.number_of_errors >= 1:
                if self.error.number_of_errors == 1:
                    self.display_line(self.screen.y_max - 2, 0, self.error.text, Color.IMPORTANT)
                else:
                    self.display_line(self.screen.y_max - 2, 0, MSG_ERRORS, Color.IMPORTANT)
            else:
                self.display_line(self.screen.y_max - 2, 0, MSG_INPUT, Color.HINTS)

            self.error.clear_buffer()


class SeparatorView(View):
    """Display the separator in the split screen"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def render(self):
        """Render this view on the screen"""
        _, x_max = self.stdscr.getmaxyx()
        x_separator = x_max - self.screen.journal_pane_width
        y_cell = (self.screen.y_max - 3) // 6
        height = self.screen.number_of_weeks * y_cell + 2
        for row in range(height):
            self.display_line(row, x_separator, cf.SEPARATOR_ICON, Color.SEPARATOR)

##################### SCREENS ##########################


class JournalScreenView(View):
    def __init__(self, stdscr, y, x, user_tasks, screen):
        super().__init__(stdscr, y, x)
        self.user_tasks = user_tasks
        self.screen = screen

    def render(self):
        """Journal view showing all tasks"""
        self.screen.currently_drawn = AppState.JOURNAL
        if self.screen.x_max < 6 or self.screen.y_max < 3:
            return

        # Display header and footer:
        header_view = HeaderView(self.stdscr, 0, 0, cf.JOURNAL_HEADER, self.screen)
        header_view.render()

        # Display the tasks:
        journal_view = JournalView(self.stdscr, 2, self.screen.x_min, self.user_tasks, self.screen)
        journal_view.render()


class WelcomeScreenView(View):
    """Welcome screen displaying greeting info on the first run"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def calibrate_position(self):
        """Depending on the screen space calculate the best position"""
        self.y_max, self.x_max = self.stdscr.getmaxyx()

    def render(self):
        """Draw the welcome screen"""
        self.calibrate_position()
        self.stdscr.clear()
        self.fill_background()

        if self.x_max < len(MSG_WELCOME_4)+2 or self.y_max < 12:
            self.display_line(0, 0, "Welcome!", Color.ACTIVE_PANE)
            return

        d_x = self.x_max//2
        d_y = self.y_max//2 - 5

        self.display_line(d_y, d_x - len(MSG_WELCOME_1+__version__+" ")//2, f"{MSG_WELCOME_1} {__version__}", Color.ACTIVE_PANE)
        self.display_line(d_y + 1, d_x - len(MSG_WELCOME_2)//2, MSG_WELCOME_2, Color.TODO)
        self.display_line(d_y + 3, d_x - len(MSG_WELCOME_3)//2, MSG_WELCOME_3, Color.TODO)
        self.display_line(d_y + 4, d_x - len(str(cf.config_folder))//2, str(cf.config_folder), Color.TITLE)
        self.display_line(d_y + 6, d_x - len(MSG_WELCOME_4)//2, MSG_WELCOME_4, Color.TODO)
        self.display_line(d_y + 7, d_x - len(MSG_SITE)//2, MSG_SITE, Color.TITLE)
        self.display_line(d_y + 9, d_x - len(MSG_WELCOME_5)//2, MSG_WELCOME_5, Color.TODO)


class HelpScreenView(View):
    """Help screen displaying information about keybindings"""

    def __init__(self, stdscr, y, x, screen):
        super().__init__(stdscr, y, x)
        self.screen = screen

    def calibrate_position(self):
        """Depending on the screen space calculate the best position"""
        self.y_max, self.x_max = self.stdscr.getmaxyx()

        if self.x_max < 102:
            self.global_shift_x = 0
            self.shift_x = 0
            self.shift_y = 6 + len(KEYS_GENERAL) + len(KEYS_CALENDAR)
        else:
            self.global_shift_x = (self.x_max - 102) // 2
            self.shift_x = 45
            self.shift_y = 2

        if self.y_max > 20 and self.x_max >= 102:
            self.global_shift_y = (self.y_max - 25) // 2
        else:
            self.global_shift_y = 0

    def render(self):
        """Draw the help screen"""
        self.calibrate_position()
        if self.x_max < 6 or self.y_max < 3:
            return
        self.stdscr.clear()
        self.fill_background()

        # Left column:
        self.display_line(self.global_shift_y, self.global_shift_x + 1, f"{MSG_NAME} {__version__}",
                            Color.ACTIVE_PANE, cf.BOLD_TITLE, cf.UNDERLINED_TITLE)
        self.display_line(self.global_shift_y + 2, self.global_shift_x + 8,
                          TITLE_KEYS_GENERAL, Color.TITLE, cf.BOLD_TITLE, cf.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_GENERAL):
            self.display_line(self.global_shift_y + index + 3, self.global_shift_x, key, Color.ACTIVE_PANE)
            self.display_line(self.global_shift_y + index + 3, self.global_shift_x + 8, KEYS_GENERAL[key], Color.TODO)

        self.display_line(self.global_shift_y + 4 + len(KEYS_GENERAL), self.global_shift_x + 8,
                          TITLE_KEYS_CALENDAR, Color.TITLE, cf.BOLD_TITLE, cf.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_CALENDAR):
            self.display_line(self.global_shift_y + index + 5 + len(KEYS_GENERAL), self.global_shift_x, key, Color.ACTIVE_PANE)
            self.display_line(self.global_shift_y + index + 5 + len(KEYS_GENERAL), self.global_shift_x + 8,
                                                                            KEYS_CALENDAR[key], Color.TODO)

        # Right column:
        d_x = self.global_shift_x + self.shift_x
        d_y = self.global_shift_y + self.shift_y
        self.display_line(d_y, d_x + 8, TITLE_KEYS_JOURNAL, Color.TITLE, cf.BOLD_TITLE, cf.UNDERLINED_TITLE)
        for index, key in enumerate(KEYS_TODO):
            self.display_line(d_y + index + 1, d_x, key, Color.ACTIVE_PANE)
            self.display_line(d_y + index + 1, d_x + 8, KEYS_TODO[key], Color.TODO)

        # Additional info:
        d_x = self.global_shift_x + self.shift_x + 8
        d_y = self.global_shift_y + len(KEYS_TODO) + self.shift_y
        self.display_line(d_y + 2, d_x, MSG_VIM, Color.ACTIVE_PANE)
        self.display_line(d_y + 4, d_x, MSG_INFO, Color.TODO)
        self.display_line(d_y + 5, d_x, MSG_SITE, Color.TITLE)


def main(stdscr) -> None:
    """Main function that runs and switches screens"""

    screen = Screen(stdscr, cf)

    # Initialise loaders:
    task_loader_csv = TaskLoaderCSV(cf)

    # Load the data:
    user_tasks = task_loader_csv.load()

    # Initialise savers and importers:
    task_saver_csv = TaskSaverCSV(user_tasks, cf)

    # Initialise terminal screen:
    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(False)

    initialize_colors(cf)

    # Initialise screen views:
    app_view = View(stdscr, 0, 0)
    journal_screen_view = JournalScreenView(stdscr, 0, 0, user_tasks, screen)
    help_screen_view = HelpScreenView(stdscr, 0, 0, screen)
    welcome_screen_view = WelcomeScreenView(stdscr, 0, 0, screen)
    footer_view = FooterView(stdscr, 0, 0, screen)
    separator_view = SeparatorView(stdscr, 0, 0, screen)
    error_view = ErrorView(stdscr, 0, 0, screen)

    # Show welcome screen on the first run:
    if cf.is_first_run:
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
            curses.halfdelay(cf.REFRESH_INTERVAL * 10)

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

        else:
            break

        # If something has been changed, save the data:
        if user_tasks.changed:
            task_saver_csv.save()
            screen.refresh_now = True

        # If needed, reload the data:
        if screen.is_time_to_reload:
            user_tasks = task_loader_csv.load()

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

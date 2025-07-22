import curses

from calcuresu.colors import Color


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
                color = color.value if hasattr(color, "value") else color
                self.stdscr.addstr(y, x, text, curses.color_pair(color))
        except curses.error: # Fix for occasional error with large zoom (reason is unclear)
            return

from calcuresu.base_view import View
from calcuresu.classes.task import TaskFilter
from calcuresu.colors import Color


class FilterView(View):
    """Display the filter of the journal"""

    def __init__(self, stdscr, y, x, user_filter: TaskFilter):
        super().__init__(stdscr, y, x)
        self._task_filter = user_filter

    def render(self):
        """Render this view on the screen"""
        title_message = f"/ Filter: {self._task_filter} /"
        self.display_line(self.y, self.x, color=Color.TITLE, bold=True, text=title_message)


from calcure.base_view import View
from calcure.colors import Color
from calcure.singletons import global_config

class TaskDeadlineView(View):
    """Display deadline for a task"""

    def __init__(self, stdscr, y, x, task):
        super().__init__(stdscr, y, x)
        self.task = task
        self.color = Color.DEADLINES
        self.icon = global_config.DEADLINE_ICON
        self.info = f"{self.task.year}/{self.task.month}/{self.task.day}"
        self.has_deadline = (self.task.year > 0)

    def render(self):
        """Render a line with the deadline date and icon"""
        if self.has_deadline:
            self.display_line(self.y, self.x, f"{self.icon} {self.info}", self.color)

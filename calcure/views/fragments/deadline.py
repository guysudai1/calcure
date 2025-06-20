
from calcure.base_view import View
from calcure.classes.task import Task
from calcure.colors import Color
from calcure.singletons import global_config

class TaskDeadlineView(View):
    """Display deadline for a task"""

    def __init__(self, stdscr, y, x, task: Task):
        super().__init__(stdscr, y, x)
        self.task = task
        self.color = Color.DEADLINES

    def render(self):
        """Render a line with the deadline date and icon"""
        if self.task.has_deadline:
            self.display_line(self.y, self.x, f"{self.task.deadline}", self.color)

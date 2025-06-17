
from calcure.base_view import View
from calcure.colors import Color
from calcure.singletons import global_config

class TimerView(View):
    """Display timer for a task"""

    def __init__(self, stdscr, y, x, timer):
        super().__init__(stdscr, y, x)
        self.timer = timer
        self.color = Color.TIMER if self.timer.is_counting else Color.TIMER_PAUSED

    @property
    def icon(self):
        """Return icon corresponding to timer state"""
        TIMER_RUNS_ICON = "⏵" if global_config.DISPLAY_ICONS else "·"
        TIMER_PAUSED_ICON = "⏯︎" if global_config.DISPLAY_ICONS else "·"
        return TIMER_RUNS_ICON if self.timer.is_counting else TIMER_PAUSED_ICON

    def render(self):
        """Render a line with a timer and icon"""
        if self.timer.is_started:
            self.display_line(self.y, self.x, f"{self.icon} {self.timer.passed_time}", self.color)

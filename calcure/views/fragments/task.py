
from calcure.base_view import View
from calcure.classes.task import Task
from calcure.colors import Color
from calcure.data import Status
from calcure.singletons import global_config
from calcure.views.fragments.deadline import TaskDeadlineView
from calcure.views.fragments.timer import TimerView

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
        match self.task.status:
            case Status.NOT_STARTED:
                return Color.NOT_STARTED
            case Status.WIP:
                return Color.WIP
            case Status.CURRENT_MISSION:
                return Color.CURRENT_MISSION
            case Status.WAITING:
                return Color.WAITING
            case Status.DONE:
                return Color.DONE
            case _:
                raise NotImplementedError("Unrecognized status")

    @property
    def icon(self):
        """Select the icon for the task"""
        icon = global_config.TODO_ICON

        if self.task.collapse:
            icon = "+"

        return icon

    @property
    def info(self):
        """Icon and name of the task, which is decorated if needed"""
        name = self.task.name
        if self.screen.privacy or self.task.privacy:
            return f'{global_config.PRIVACY_ICON * len(name)}'

        if global_config.DISPLAY_ICONS:
            for keyword in global_config.CUSTOM_ICONS:
                icon = global_config.CUSTOM_ICONS[keyword]
                keyword = f"@{keyword}"
                name = name.replace(keyword, icon)

        if self.task.status == Status.DONE and global_config.STRIKETHROUGH_DONE:
            strike = "\u0336"
            info_str = f'{strike}{strike.join(name)}{strike}'
        else:
            info_str = f'{name}'

        if self.task.archive_date:
            info_str += f" (Archived on: {self.task.archive_date})"

        if self.task.collapse:
            info_str += f" {global_config.COLLAPSED_ICON}"

        return info_str

    def render(self):
        """Render a line with an icon, task, deadline, and timer"""
        icon_indent = self.x + self.task_indent + 4
        self.display_line(self.y, icon_indent, self.icon, Color.PROMPTS)
        importance_indent = icon_indent + 2
        self.display_line(self.y, importance_indent, f"({self.task.importance.value})", Color.IMPORTANCE)
        max_importance = "(10) "

        self.display_line(self.y, importance_indent + len(max_importance), self.info, self.color)

        deadline_indentation = self.screen.x_min + 6 + len(self.info) + self.task_indent
        deadline_view = TaskDeadlineView(self.stdscr, self.y, deadline_indentation, self.task)
        deadline_view.render()

        addition_indentation = (deadline_view.has_deadline)*(4 + len(deadline_view.info))
        timer_indentation = deadline_indentation + addition_indentation
        timer_view = TimerView(self.stdscr, self.y, timer_indentation, self.task.timer)
        timer_view.render()


from calcure.base_view import View
from calcure.classes.task import RootTask, Task
from calcure.classes.workspace import Workspace
from calcure.colors import Color
from calcure.data import Status, Workspaces
from calcure.singletons import global_config
from calcure.translations.en import MSG_TS_NO_WORKSPACES
from calcure.views.fragments.deadline import TaskDeadlineView
from calcure.views.fragments.timer import TimerView

class WorkspaceView(View):
    """Display a single workspace"""

    def __init__(self, stdscr, y, x, workspace: Workspace, screen):
        super().__init__(stdscr, y, x)
        self.workspace = workspace
        self.screen = screen

    def render(self):
        """Render a line with an icon, task, deadline, and timer"""
        icon_indent = self.x + 4
        self.display_line(self.y, icon_indent, global_config.TODO_ICON, Color.PROMPTS)

        self.display_line(self.y, icon_indent, self.workspace.workspace_path, Color.WORKSPACE)

class WorkspaceManagerView(View):
    """Display the entire workspace list"""

    def __init__(self, stdscr, y, x, workspace: Workspaces, screen):
        super().__init__(stdscr, y, x)
        self.workspaces = workspace
        self.screen = screen

    def render(self):
        """Render a line with an icon, task, deadline, and timer"""

        if not self.workspaces.workspaces:
            self.display_line(self.y, self.x, MSG_TS_NO_WORKSPACES, Color.UNIMPORTANT)
            self.y += 1
        
        for index, workspace in enumerate(self.workspaces.workspaces):
            if self.y + 1 >= self.screen.y_max:
                break

            workspace_view = WorkspaceView(self.stdscr, self.y, self.x, workspace, self.screen)
            workspace_view.render()
            if self.screen.selection_mode:
                self.display_line(self.y, self.x, str(index + 1), Color.ACTIVE_PANE)
            self.y += 1
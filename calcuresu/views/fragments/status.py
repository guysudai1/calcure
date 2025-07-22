from typing import List
from calcuresu.base_view import View
from calcuresu.classes.workspace import Workspace
from calcuresu.colors import Color
from calcuresu.data import Workspaces
from calcuresu.singletons import global_config

class TaskStatusView(View):
    """Display the status bar of the journal"""

    SEPERATOR_SIZE = 2

    def __init__(self, stdscr, y, x, screen, relevant_task_list, all_tasks):
        super().__init__(stdscr, y, x)
        self.screen = screen
        self._relevant_task_list = relevant_task_list
        self._all_tasks = all_tasks

    def render(self):
        """Render this view on the screen"""
        title_message = f"# Tasks displayed: {len(self._relevant_task_list)}/{len(self._all_tasks)}. Offset: {self.screen.offset}. Status colors:"
        self.display_line(self.y, self.x, color=Color.TITLE, bold=True, text=title_message)

        not_started_status = f"Not started yet" 
        not_started_indent = self.x + len(title_message) + self.SEPERATOR_SIZE
        self.display_line(self.y,not_started_indent, color=Color.NOT_STARTED, bold=True, text=not_started_status)

        wip_status = f"Work in progress" 
        wip_indent = not_started_indent + len(not_started_status) + self.SEPERATOR_SIZE
        self.display_line(self.y,wip_indent, color=Color.WIP, bold=True, text=wip_status)

        current_mission_status = f"Current mission" 
        current_mission_indent = wip_indent + len(wip_status) + self.SEPERATOR_SIZE
        self.display_line(self.y,current_mission_indent, color=Color.CURRENT_MISSION, bold=True, text=current_mission_status)

        waiting_status = f"Waiting" 
        waiting_indent = current_mission_indent + len(current_mission_status) + self.SEPERATOR_SIZE
        self.display_line(self.y,waiting_indent, color=Color.WAITING, bold=True, text=waiting_status)

        done_status = f"Done" 
        done_indent = waiting_indent + len(waiting_status) + self.SEPERATOR_SIZE
        self.display_line(self.y,done_indent, color=Color.DONE, bold=True, text=done_status)


class WorkspaceStatusView(View):
    """Display the status bar of the workspace manager"""

    def __init__(self, stdscr, y, x, screen, workspaces: Workspaces):
        super().__init__(stdscr, y, x)
        self.screen = screen
        self._workspace_list = workspaces

    def render(self):
        """Render this view on the screen"""
        title_message = f"# Workspaces: {len(self._workspace_list.workspaces)}"
        self.display_line(self.y, self.x, color=Color.TITLE, bold=True, text=title_message)
        
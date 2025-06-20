from datetime import timedelta
import logging
from pathlib import Path
import shelve
from typing import List

from flufl.lock import Lock
from calcure.base_view import View
from calcure.classes.workspace import Workspace
from calcure.colors import Color
from calcure.consts import VERSION
from calcure.data import Workspaces
from calcure.screen import Screen
from calcure.translations.en import MSG_SITE, MSG_TS_NO_WORKSPACES, MSG_WELCOME_1, MSG_WELCOME_2, MSG_WELCOME_3, MSG_WELCOME_4, MSG_WELCOME_5
from calcure.singletons import global_config
from calcure.singletons import error
from calcure.views.fragments.header import HeaderView
from calcure.views.fragments.status import WorkspaceStatusView
from calcure.views.fragments.workspace import WorkspaceManagerView, WorkspaceView

class WorkspaceManagerScreenView(View):
    """Workspace manager/wizard for creating new workspaces"""

    def __init__(self, stdscr, y, x, screen: Screen, workspaces: Workspaces):
        super().__init__(stdscr, y, x)
        self.screen = screen
        self.workspaces = workspaces
    
    def render(self):
        """Draw the welcome screen"""
        self.workspaces.save_if_needed()

        self.stdscr.clear()
        self.fill_background()

        header_view = HeaderView(self.stdscr, self.y, self.x, "Workspace Manager", self.screen)
        header_view.render()

        if self.y == 0:
            self.y += 1
        
        workspace_status = WorkspaceStatusView(self.stdscr, self.y, self.x, self.screen, self.workspaces)
        workspace_status.render()

        workspace_view = WorkspaceManagerView(self.stdscr, self.y + 1, self.x, self.workspaces, self.screen)
        workspace_view.render()

        self.stdscr.refresh()


        

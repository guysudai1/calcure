"""This module contains functions that react to user input on each screen"""

from asyncio import Timeout, tasks
import curses
import dbm.sqlite3
import dbm.sqlite3
import importlib

# Modules:
from calcuresu.classes.task import Task
from calcuresu.classes.timer import Timer
from calcuresu.consts import AppState, Status
from calcuresu.data import *
from calcuresu.data import Tasks
from calcuresu.dialogues import *
from calcuresu.configuration import Config
from calcuresu.screen import Screen

global_config = Config()

# Language:
from calcuresu.translations.en import *


def safe_run(func):
    """Decorator preventing crashes on keyboard interruption and no input"""

    def inner(stdscr, screen, *args, **kwargs):
        try:
            return func(stdscr, screen, *args, **kwargs)

        # Handle keyboard interruption with ctrl+c:
        except KeyboardInterrupt:
            confirmed = ask_confirmation(stdscr, screen, MSG_EXIT)
            screen.state = AppState.EXIT if confirmed else screen.state
            return None

        except curses.error:
            return None

    return inner


HEADER_FIELD_COUNT = 2

def handle_screen_movement(screen: Screen, key: str|None):
    if key in ["KEY_DOWN"]:
        screen.change_offset_forwards(step_count=1)
        screen.next_need_refresh = True
    elif key in ["KEY_UP"]:
        screen.change_offset_backwards(step_count=1)
        screen.next_need_refresh = True
    elif key in ["KEY_PPAGE"]:
        screen.change_offset_backwards(step_count=6)
        screen.next_need_refresh = True
    elif key in ["KEY_NPAGE"]:
        screen.change_offset_forwards(step_count=6)
        screen.next_need_refresh = True

def handle_screen_transfer_keys(stdscr, screen: Screen, key: str|None, quit_state=AppState.EXIT):
    if key is None:
        return False

    if key == "q":
        confirmed = ask_confirmation(stdscr, screen, MSG_EXIT)
        if confirmed:
            screen.state = quit_state
            return True
    
    if key == "?":
        screen.state = AppState.HELP
        screen.next_need_refresh = True
        return True
    
    if key == ' ':
        displayable_windows = [AppState.JOURNAL, AppState.ARCHIVE]
        if screen.state in displayable_windows:
            state_index = displayable_windows.index(screen.state)
            screen.state = displayable_windows[(state_index + 1) % len(displayable_windows)]
            screen.next_need_refresh = True
            return True

    if not key.isdigit():
        return False

    try:
        new_state = AppState(int(key))
        screen.state = new_state
        screen.next_need_refresh = True
        return True
    except ValueError:
        logging.error("Invalid new state")

    return False

def handle_reload_keys(screen: Screen, key: str|None):
    # Reload:
    if key in ["Q"]:
        screen.reload_data = True
        screen.refresh_now = True
        screen.next_need_refresh = True



def nonblocking_getkey(stdscr: curses.window):
    
    try:
        curses.cbreak()
        stdscr.nodelay(True)
        return stdscr.getkey()
    finally:
        curses.halfdelay(20)    

@safe_run
def control_journal_screen(stdscr: curses.window, screen: Screen, user_tasks: Tasks):
    """Process user input on the journal screen"""
        
    # If we previously selected a task, now we perform the action:
    if screen.selection_mode:

        with try_to_lock_auto_unlock(stdscr, screen, user_tasks) as lock_successful:
            if lock_successful:            
                # Collapse/Expand
                if screen.key == 'c':
                    number = input_integer(stdscr, screen, MSG_TS_COLLAPSE)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.toggle_task_collapse(task)

                # Modify extra info
                if screen.key == 'o':
                    number = input_integer(stdscr, screen, MSG_TS_EXTRA_INFO_TASK)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.edit_and_display_extra_info(task, stdscr)

                # Timer operations:
                if screen.key == 't':
                    number = input_integer(stdscr, screen, MSG_TM_ADD)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.add_timestamp_for_task(task)

                if screen.key == 'T':
                    number = input_integer(stdscr, screen, MSG_TM_RESET)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.reset_timer_for_task(task)

                # Add deadline:
                if screen.key == "f":
                    number = input_integer(stdscr, screen, MSG_TS_DEAD_ADD)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        deadline_date = input_date(stdscr, screen, MSG_TS_DEAD_DATE)
                        user_tasks.change_deadline(task, deadline_date)

                # Remove deadline:
                if screen.key == "F":
                    number = input_integer(stdscr, screen, MSG_TS_DEAD_DEL)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.change_deadline(task, None)

                # Change the importance:
                if screen.key == 'i':
                    number = input_integer(stdscr, screen, MSG_TS_IMPORTANCE)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        new_importance = input_importance(stdscr, screen)
                        if new_importance is not None:
                            user_tasks.change_item_importance(task, new_importance)
                
                # Change the status:
                if screen.key == 's':
                    number = input_integer(stdscr, screen, MSG_TS_STATUS)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        new_status = input_status(stdscr, screen)
                        if new_status is not None:
                            user_tasks.change_item_status(task, new_status)
                
                if screen.key == 'd':
                    number = input_integer(stdscr, screen, MSG_TS_DONE)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.change_item_status(task, Status.DONE)

                # Toggle task privacy:
                if screen.key == '.':
                    number = input_integer(stdscr, screen, MSG_TS_PRIVACY)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]
                        user_tasks.toggle_item_privacy(task)

                # Modify the task:
                if screen.key in ['x']:
                    msg = MSG_TS_DEL
                    if global_config.ADD_TO_ARCHIVE_ON_DELETE.value:
                        msg = MSG_TS_ARCHIVE
                    number = input_integer(stdscr, screen, msg)
                    if number is not None and user_tasks.is_valid_number(number):
                        task: Task = user_tasks.viewed_ordered_tasks[number]
                        if task.children:
                            msg = MSG_TS_CHILDREN_DEL
                            if global_config.ADD_TO_ARCHIVE_ON_DELETE.value:
                                msg = MSG_TS_CHILDREN_ARCHIVE

                            delete_children_as_well = ask_confirmation(stdscr, screen, msg)
                        else:
                            delete_children_as_well = False
                        
                        if global_config.ADD_TO_ARCHIVE_ON_DELETE.value:
                            user_tasks.archive_task(task.item_id, delete_children_as_well)
                        else:
                            user_tasks.delete_task(task.item_id, delete_children_as_well)

                if screen.key == 'm':
                    number_from = input_integer(stdscr, screen, MSG_TS_MOVE)
                    if number_from is not None and user_tasks.is_valid_number(number_from):
                        number_to = input_integer(stdscr, screen, MSG_TS_MOVE_TO)

                        if number_to is not None and (user_tasks.is_valid_number(number_to) or number_to == -1):
                            src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                            if number_to == -1:
                                move_dest_task = user_tasks.root_task
                            else:
                                move_dest_task = user_tasks.viewed_ordered_tasks[number_to]

                            user_tasks.move_task(src_task, move_dest_task)

                if screen.key == 'r':
                    number = input_integer(stdscr, screen, MSG_TS_EDIT)
                    if number is not None and user_tasks.is_valid_number(number):
                        task = user_tasks.viewed_ordered_tasks[number]

                        new_name = input_string(stdscr, screen, MSG_TS_RENAME_TASK,
                                                placeholder=MSG_TS_INPUT_TASK,
                                                default=task.name, autocomplete=global_config.icon_completer)
                        if new_name:
                            user_tasks.rename_task(task, new_name)

                # Exchange operation
                if screen.key == 'e':
                    number_from = input_integer(stdscr, screen, MSG_TS_MOVE)
                    if number_from is not None and user_tasks.is_valid_number(number_from):
                        number_to = input_integer(stdscr, screen, MSG_TS_MOVE_TO)

                        if number_to is not None and user_tasks.is_valid_number(number_to):
                            src_task: Task = user_tasks.viewed_ordered_tasks[number_from]
                            swap_dest_task: Task = user_tasks.viewed_ordered_tasks[number_to]
                            user_tasks.swap_task(src_task, swap_dest_task)

                if screen.key == 'A':
                    task_number: int|None = input_integer(stdscr, screen, MSG_TS_SUB)
                    if task_number is not None and user_tasks.is_valid_number(task_number):
                        task_name = input_string(stdscr, screen, MSG_TS_TITLE, placeholder=MSG_TS_INPUT_TASK, autocomplete=global_config.icon_completer)
                        if task_name:
                            parent_task: Task = user_tasks.viewed_ordered_tasks[task_number]
                            user_tasks.add_subtask(task_name, parent_task)

                user_tasks.save_if_needed_nolock()
        
        screen.selection_mode = False

    # Otherwise, we check for user input:
    else:
        if not screen.delayed_action:
            # Wait for user to press a key:
            screen.key = nonblocking_getkey(stdscr)
            
            if handle_screen_transfer_keys(stdscr, screen, screen.key):
                return

        # If we need to select a task, change to selection mode:
        selection_keys = ['t', 'T', 'u', 'i', 's', 'd', 'x', 'e', 'r', 'c', 'A', 'm', '.', 'f', 'F', 'o']
        if screen.key in selection_keys and user_tasks.viewed_ordered_tasks:
            screen.selection_mode = True
            screen.next_need_refresh = True
            return

        # Add single task:
        if screen.key == "a":
            # TODO: Lower the screen offset if we're close to the edge
            if screen.delayed_action:
                # We delayed the action to move the offset
                screen.delayed_action = False

            amount_of_elements_on_screen = len(user_tasks.viewed_ordered_tasks[screen.offset:])
            if amount_of_elements_on_screen >= screen.y_max - HEADER_FIELD_COUNT - 1:
                # This means that we have more elements on the screen and we are at the edge
                amount_of_elements_on_screen = 5
                screen.offset = len(user_tasks.viewed_ordered_tasks) - amount_of_elements_on_screen
                screen.refresh_now = True
                screen.delayed_action = True
                return

            with try_to_lock_auto_unlock(stdscr, screen, user_tasks) as lock_successful:
                if lock_successful:            
                    task_name = input_string(stdscr, screen, MSG_TS_NEW_TASK, placeholder=MSG_TS_INPUT_TASK, autocomplete=global_config.icon_completer)
                    if task_name:
                        task_id = user_tasks.generate_id()
                        user_tasks.add_item(Task(task_id, task_name, Status.NOT_STARTED, [], False, parent_id=0))
                    user_tasks.save_if_needed_nolock()

        if screen.key == "/":
            filter_chosen = input_filter_field(stdscr, screen, MSG_TS_FILTER, placeholder="Leave this empty to clear the filter", display_error=True)
            if filter_chosen is not None:
                filter_content = input_filter_content(stdscr, screen, filter_chosen)
                new_filter = TaskFilter(filter_chosen, filter_content)
                user_tasks.filter = new_filter
            else:
                user_tasks.clear_filter()

        # Bulk operations:
        if screen.key in ["X"]:
            with try_to_lock_auto_unlock(stdscr, screen, user_tasks) as lock_successful:
                if lock_successful:
                    confirmed = ask_confirmation(stdscr, screen, MSG_TS_DEL_ALL)
                    if confirmed:
                        user_tasks.delete_all_items()
                    user_tasks.save_if_needed_nolock()

        handle_screen_movement(screen, screen.key)

        # Reload:
        handle_reload_keys(screen, screen.key)

@safe_run
def control_help_screen(stdscr, screen):
    """Process user input on the help screen"""
    # Getting user's input:
    screen.key = nonblocking_getkey(stdscr)

    handle_reload_keys(screen, screen.key)
    handle_screen_transfer_keys(stdscr, screen, screen.key, quit_state=AppState.WIZARD)

@safe_run
def control_color_screen(stdscr, screen):
    """Process user input on the help screen"""
    # Getting user's input:
    screen.key = nonblocking_getkey(stdscr)

    handle_reload_keys(screen, screen.key)
    handle_screen_transfer_keys(stdscr, screen, screen.key)


@safe_run
def control_welcome_screen(stdscr, screen):
    """Process user input on the welcome screen"""
    # Getting user's input:
    screen.key = nonblocking_getkey(stdscr)

    handle_reload_keys(screen, screen.key)
    handle_screen_transfer_keys(stdscr, screen, screen.key, quit_state=AppState.WIZARD)
    
@safe_run
def control_archive_screen(stdscr: curses.window, screen: Screen, user_tasks: Tasks):
    """Process user input on the welcome screen"""
    
    if screen.selection_mode:
        screen.selection_mode = False

        with try_to_lock_auto_unlock(stdscr, screen, user_tasks) as lock_successful:
            if lock_successful:            
                if screen.key == "x":
                    number = input_integer(stdscr, screen, MSG_TS_RES)
                    if number is not None and user_tasks.is_valid_archive_number(number):
                        task: Task = user_tasks.viewed_archived_ordered_tasks[number]
                        if task.children:
                            restore_children_as_well = ask_confirmation(stdscr, screen, "Restore all children too?")
                        else:
                            restore_children_as_well = False
                        
                        user_tasks.restore_item_from_archive_with_children(task, restore_children_as_well)

                # Modify extra info
                if screen.key == 'o':
                    number = input_integer(stdscr, screen, MSG_TS_EXTRA_INFO_TASK)
                    if number is not None and user_tasks.is_valid_archive_number(number):
                        task = user_tasks.viewed_archived_ordered_tasks[number]
                        user_tasks.edit_and_display_extra_info(task, stdscr)

                user_tasks.save_if_needed_nolock()
    else:
        # Getting user's input:
        screen.key = nonblocking_getkey(stdscr)

        if screen.key in ["x", "o"]:
            screen.selection_mode = True
            screen.next_need_refresh = True
            return

        if screen.key == "/":
            filter_chosen = input_filter_field(stdscr, screen, MSG_TS_FILTER, placeholder="Leave this empty to clear the filter", display_error=True)
            if filter_chosen is not None:
                filter_content = input_filter_content(stdscr, screen, filter_chosen)
                new_filter = TaskFilter(filter_chosen, filter_content)
                user_tasks.filter = new_filter
            else:
                user_tasks.clear_filter()

            screen.next_need_refresh = True

        handle_screen_movement(screen, screen.key)
        handle_reload_keys(screen, screen.key)
        handle_screen_transfer_keys(stdscr, screen, screen.key)


@safe_run
def control_workspaces_screen(stdscr: curses.window, screen: Screen, workspaces: Workspaces) -> Tasks | None:
    """Process user input on the welcome screen"""
    
    if screen.selection_mode:
        screen.selection_mode = False
        screen.next_need_refresh = True

        with try_to_lock_auto_unlock(stdscr, screen, workspaces) as lock_successful:
            if lock_successful:      
                # Delete workspace
                if screen.key == "x":
                    number = input_integer(stdscr, screen, MSG_WS_DEL)
                    if number is not None and workspaces.is_valid_number(number):
                        workspace: Workspace = workspaces.workspaces[number]
                        
                        delete_files = ask_confirmation(stdscr, screen, "Delete files? (Warning: this can not be reverted)")
                        workspaces.delete_workspace(workspace, delete_files)

                # Load workspace
                if screen.key == 'l':
                    number = input_integer(stdscr, screen, MSG_WS_LOAD)
                    if number is not None and workspaces.is_valid_number(number):
                        workspace: Workspace = workspaces.workspaces[number]
                        
                        workspaces.workspace_loaded = workspace
                        try:
                            user_tasks: Tasks | None = Tasks.from_workspace(workspace)
                            if not user_tasks.initialize(stdscr, screen):
                                user_tasks: Tasks | None = None
                                logging.warning("Did not acquire the initialization lock. Try again soon")
                                return    
                            screen.state = AppState.JOURNAL
                        except dbm.error:
                            user_tasks: Tasks | None = None

                        return user_tasks
            
                workspaces.save_if_needed_nolock()
        
    else:
        # Getting user's input:
        screen.key = nonblocking_getkey(stdscr)

        if screen.key in ["x", "l"]:
            screen.selection_mode = True
            screen.next_need_refresh = True
            return

        handle_screen_movement(screen, screen.key)
        handle_reload_keys(screen, screen.key)
        handle_screen_transfer_keys(stdscr, screen, screen.key)

        # Add single task:
        if screen.key == "a":
            if screen.delayed_action:
                # We delayed the action to move the offset
                screen.delayed_action = False

            amount_of_elements_on_screen = len(workspaces.workspaces[screen.offset:])
            if amount_of_elements_on_screen >= screen.y_max - HEADER_FIELD_COUNT - 1:
                # This means that we have more elements on the screen and we are at the edge
                amount_of_elements_on_screen = 5
                screen.offset = len(workspaces.workspaces) - amount_of_elements_on_screen
                screen.refresh_now = True
                screen.delayed_action = True
                return
            
            with try_to_lock_auto_unlock(stdscr, screen, workspaces) as lock_successful:
                if lock_successful:      
                    workspace_path = input_path(stdscr, screen, MSG_WS_NEW_WORKSPACE, placeholder=MSG_WS_NEW_WORKSPACE_TIP)
                    if workspace_path:
                        workspaces.add_workspace(Workspace(workspace_path))

                    workspaces.save_if_needed_nolock()

            screen.next_need_refresh = True


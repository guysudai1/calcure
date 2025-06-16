"""Module provides datatypes used in the program"""

from asyncio.base_tasks import _task_get_stack
import datetime
import logging
from operator import index
from textwrap import indent
import time
import enum
from typing import List

from dateutil.rrule import rruleset, rrulestr
from calcure.calendars import Calendar


class AppState(enum.Enum):
    """Possible focus states of the application"""
    CALENDAR = 1
    JOURNAL = 2
    HELP = 3
    EXIT = 4
    WELCOME = 5


class CalState(enum.Enum):
    """Possible states of the calendar view"""
    MONTHLY = 1
    DAILY = 2


class Status(enum.Enum):
    """Status of events and tasks"""
    NORMAL = 1
    DONE = 2
    IMPORTANT = 3
    UNIMPORTANT = 4


class Frequency(enum.Enum):
    """Frequency of repetitions of recurring events"""
    ONCE = 1
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4
    YEARLY = 5


class Task:
    """Tasks created by the user"""

    def __init__(self, item_id, name, status, timer, privacy, parent_id, year=0, month=0, day=0, calendar_number=None):
        self.item_id = item_id
        self.name = name
        self.status = status
        self.timer = timer
        self.privacy = privacy
        self.year = year
        self.month = month
        self.day = day
        self.calendar_number = calendar_number
        self.parent_id = parent_id
        self.children: List[Task] = []

    def __eq__(self, other):
        return self.item_id == other.item_id

class RootTask:
    """
    This is a fake item to use as the root of all other tasks
    """
    def __init__(self, task_tree: List[Task]) -> None:
        self.item_id = 0
        self.name = "FAKE ROOT ITEM"
        self.children = task_tree  # Reference to the task tree

    @property 
    def parent_id(self):
        raise Exception("Root task has no parent id")
    
    def __eq__(self, other):
        return self.item_id == other.item_id

class Event:
    """Parent class of all events"""

    def __init__(self, year, month, day, name):
        self.year = year
        self.month = month
        self.day = day
        self.name = name


class UserEvent(Event):
    """Events created by the user"""

    def __init__(self, item_id, year, month, day, name, repetition, frequency, status, privacy,
                                                    calendar_number=None, hour=None, minute=None, rrule=None, exdate=None):
        super().__init__(year, month, day, name)
        self.item_id = item_id
        self.repetition = repetition
        self.frequency = frequency
        self.status = status
        self.privacy = privacy
        self.calendar_number = calendar_number
        self.hour = hour
        self.minute = minute
        self.rrule = rrule
        self.exdate = exdate

    def getDatetime(self):
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        return datetime.datetime(self.year, self.month, self.day, self.hour or 0, self.minute or 0, tzinfo=local_timezone)


class UserRepeatedEvent(Event):
    """Events that are repetitions of the original user events"""

    def __init__(self, item_id, year, month, day, name, status, privacy, calendar_number=None):
        super().__init__(year, month, day, name)
        self.item_id = item_id
        self.status = status
        self.privacy = privacy
        self.calendar_number = calendar_number


class Timer:
    """Timer for tasks"""

    def __init__(self, stamps):
        self.stamps = stamps

    @property
    def is_counting(self):
        """Evaluate if the timer is currently running"""
        return False if not self.stamps else (len(self.stamps)%2 == 1)

    @property
    def is_started(self):
        """Evaluate whether the timer has started"""
        return True if self.stamps else False

    @property
    def passed_time(self):
        """Calculate how much time has passed in the un-paused intervals"""
        time_passed = 0

        # Calculate passed time, assuming that even timestamps are pauses:
        for index, _ in enumerate(self.stamps):
            if index > 0 and index % 2 == 1:
                time_passed += float(self.stamps[index]) - float(self.stamps[index-1])

        # Add time passed during the current run:
        if self.is_counting:
            time_passed += time.time() - float(self.stamps[-1])

        # Depending on how much time has passed, show in different formats:
        one_hour = 60*60.0
        one_day = 24*one_hour
        if time_passed < one_hour:
            format_string = "%M:%S"
        else:
            format_string = "%H:%M:%S"
        time_string = str(time.strftime(format_string, time.gmtime(int(time_passed))))

        if 2*one_day > time_passed > one_day:
            time_string = "1 day " + time_string
        if time_passed >= 2*one_day:
            time_string = str(int(time_passed//one_day)) + " days " + time_string
        return time_string


class Collection:
    """Parent class for collections of items like tasks or events"""

    def __init__(self):
        self.items: List[Task] = []
        self.changed = False

    def add_item(self, item):
        """Add an item to the collection"""
        if 1000 > len(item.name) > 0 and item.name != r"\[":
            self.items.append(item)
            self.changed = True

    def delete_item(self, selected_task_id):
        """Delete an item with provided id from the collection"""
        for item in self.items:
            if item.item_id == selected_task_id:
                self.items.remove(item)
                self.changed = True
                break

    def rename_item(self, selected_task_id, new_name):
        """Edit an item name in the collection"""
        for item in self.items:
            if item.item_id == selected_task_id and len(new_name) > 0:
                item.name = new_name
                self.changed = True

    def toggle_item_status(self, selected_task_id, new_status):
        """Toggle the status for the item with provided id"""
        for item in self.items:
            if item.item_id == selected_task_id:
                if item.status == new_status:
                    item.status = Status.NORMAL
                else:
                    item.status = new_status
                self.changed = True
                break

    def toggle_item_privacy(self, selected_task_id):
        """Toggle the privacy for the item with provided id"""
        for item in self.items:
            if item.item_id == selected_task_id:
                item.privacy = not item.privacy
                self.changed = True
                break

    def item_exists(self, item_name):
        """Check if such item already exists in collection"""
        for item in self.items:
            if item.name == item_name:
                return True
        return False

    def change_all_statuses(self, new_status):
        """Change statuses of all items"""
        for item in self.items:
            item.status = new_status
            self.changed = True

    def delete_all_items(self):
        """Delete all items from the collection"""
        self.items.clear()
        self.changed = True

    def is_empty(self):
        """Check if the collection is empty"""
        return len(self.items) == 0

    def is_valid_number(self, number):
        """Check if input is valid and corresponds to an item"""
        if number is None:
            return False
        return 0 <= number < len(self.items)

    def filter_events_that_day(self, screen):
        """Filter only events that happen on the particular day"""
        events_of_the_day = Events()
        for event in self.items:
            if (event.year == screen.year
                and event.month == screen.month
                and event.day == screen.day):
                events_of_the_day.add_item(event)
        return events_of_the_day

    def filter_events_that_month(self, screen):
        """Filter only events that happen on the particular month and sort them by day"""
        events_of_the_month = Events()
        for event in self.items:
            if event.month == screen.month and event.year == screen.year:
                events_of_the_month.add_item(event)
        events_of_the_month.items = sorted(events_of_the_month.items, key=lambda item: item.day)
        return events_of_the_month


class Tasks(Collection):
    """List of tasks created by the user"""

    def __init__(self):
        super().__init__()
        self.task_tree: List[Task] = []
        self._root_task = RootTask(self.task_tree)

    def delete_all_items(self):
        self.task_tree.clear()
        return super().delete_all_items()

    @property
    def ordered_tasks(self):
        task_list = []

        for task in self.task_tree:
            task_list.append(task)
            task_list.extend(self.flatten_children_ordered(task))

        return task_list
    
    def delete_task(self, task_id, delete_children):
        assert task_id != 0, "Cannot delete root task"

        task_to_remove = self.get_task_by_id(task_id)
        self._delete_task_from_parents(task_to_remove)        

        for child_task in task_to_remove.children:
            if not delete_children:
                self.update_parent(child_task, task_to_remove.parent_id, delete_from_parent=False)
            elif delete_children:
                super().delete_item(child_task.item_id)

        super().delete_item(task_to_remove.item_id)

        self.changed = True
        
    def _delete_task_from_parents(self, task: Task):
        parent_task = self.get_task_by_id(task.parent_id)
        parent_task.children.remove(task)
        self.changed = True

    def get_indent_count(self, task):
        indent = 0
        while task.parent_id != 0:
            indent += 1
            task = self.get_task_by_id(task.parent_id)
    
        return indent

    def get_task_by_id(self, task_id):
        if task_id == 0:
            return self._root_task

        for task in self.items:
            if task.item_id == task_id:
                return task 
        raise ValueError()

    def update_parent(self, item: Task, new_parent_id: int, delete_from_parent: bool):
        if delete_from_parent:
            self._delete_task_from_parents(item)

        item.parent_id = new_parent_id
        parent_task = self.get_task_by_id(item.parent_id)
        parent_task.children.append(item)
        self.changed = True

    def add_item(self, item: Task):
        parent_task = self.get_task_by_id(item.parent_id)
        parent_task.children.append(item)
        self.changed = True

        return super().add_item(item)

    @property
    def has_active_timer(self):
        for item in self.items:
            if item.timer.is_counting:
                return True
        return False

    def add_subtask(self, task_name, task_number):
        """Add a subtask for certain task in the journal"""
        parent_item_id = self.ordered_tasks[task_number].item_id
        child_task = Task(self.generate_id(), task_name,  Status.NORMAL, Timer([]), False, parent_id=parent_item_id)
        self.add_item(child_task)
        self.changed = True

    def add_timestamp_for_task(self, selected_task_id):
        """Add a timestamp to this task"""
        for item in self.items:
            if item.item_id == selected_task_id:
                item.timer.stamps.append(int(time.time()))
                self.changed = True
                break

    def pause_all_other_timers(self, selected_task_id):
        """Add a timestamp to this task"""
        for item in self.items:
            if item.timer.is_counting and item.item_id != selected_task_id:
                item.timer.stamps.append(int(time.time()))
                self.changed = True

    def reset_timer_for_task(self, selected_task_id):
        """Reset the timer for one of the tasks"""
        for item in self.items:
            if item.item_id == selected_task_id:
                item.timer.stamps = []
                self.changed = True
                break

    def change_deadline(self, selected_task_id, new_year, new_month, new_day):
        """Reset the timer for one of the tasks"""
        for item in self.items:
            if item.item_id == selected_task_id:
                item.year = new_year
                item.month = new_month
                item.day = new_day
                self.changed = True
                break

    def flatten_children_ordered(self, parent_task: Task):
        """ This returns the task list ordered by which one will be displayed first """
        flattened_list = []
        nodes_to_go_over = parent_task.children.copy()
        while nodes_to_go_over:
            current_node = nodes_to_go_over.pop(0)
            flattened_list.append(current_node)
            nodes_to_go_over = current_node.children + nodes_to_go_over

        return flattened_list

    def get_all_subtasks_for_task(self, father_task: Task, direct_subtask: bool):
        subtasks = []
        if direct_subtask:
            subtasks = father_task.children
        else:
            subtasks = self.flatten_children_ordered(father_task)
        
        return subtasks

    def is_task_child_of_other_task(self, parent_task: Task, possible_child_task: Task, direct_subtask):
        subtasks = self.get_all_subtasks_for_task(parent_task, direct_subtask)

        return possible_child_task in subtasks

    def swap_task(self, src_task: Task, dst_task: Task):
        # Get parents for both tasks
        src_task_parent = self.get_task_by_id(src_task.parent_id)
        dst_task_parent = self.get_task_by_id(dst_task.parent_id)

        src_task_index_in_parent = src_task_parent.children.index(src_task)
        dst_task_index_in_parent = dst_task_parent.children.index(dst_task)
        
        src_task_parent.children[src_task_index_in_parent] = dst_task
        dst_task_parent.children[dst_task_index_in_parent] = src_task

        src_task.parent_id = dst_task_parent.item_id
        dst_task.parent_id = src_task_parent.item_id
        self.changed = True

    def move_task(self, src_task: Task, dest_task: Task):
        """Move task from certain place to another in the list"""

        if src_task == dest_task:
            logging.error("Cannot move the task to itself")
            return
    
        if self.is_task_child_of_other_task(dest_task, src_task, direct_subtask=True):
            logging.error("Cannot move direct subtask to its parent")
            return

        if self.is_task_child_of_other_task(src_task, dest_task, direct_subtask=False):
            logging.error("Cannot move parent to its child")
            return
    
        self.update_parent(src_task, dest_task.item_id, delete_from_parent=True)
        
        self.changed = True

    def generate_id(self):
        """Generate a id for a new item. The id is generated as maximum of existing ids plus one"""
        if self.is_empty():
            return 1
        return max([item.item_id for item in self.items]) + 1


class Events(Collection):
    """List of events created by the user or imported"""

    def event_exists(self, new_event):
        """Check if such event already exists in collection"""
        for event in self.items:
            if (event.name == new_event.name
                and event.year == new_event.year
                and event.month == new_event.month
                and event.day == new_event.day):
                return True
        return False

    def change_day(self, selected_item_id, new_day):
        """Move an event to another day within this month"""
        for item in self.items:
            if item.item_id == selected_item_id:
                item.day = new_day
                self.changed = True
                break

    def change_date(self, selected_item_id, new_year, new_month, new_day):
        """Move an event to another date"""
        for item in self.items:
            if item.item_id == selected_item_id:
                item.year = new_year
                item.month = new_month
                item.day = new_day
                self.changed = True
                break

class Birthdays(Events):
    """List of birthdays imported from abook"""

    def filter_events_that_day(self, screen):
        """Filter only birthdays that happen on the particular day"""
        events_of_the_day = Events()
        for event in self.items:
            if event.month == screen.month and event.day == screen.day:
                events_of_the_day.add_item(event)
        return events_of_the_day


class RepeatedEvents(Events):
    """List of events that are repetitions of main events"""

    def __init__(self, user_events, use_persian_calendar, current_year):
        super().__init__()
        self.user_events = user_events
        self.use_persian_calendar = use_persian_calendar

        for event in self.user_events.items:
            if event.repetition >= 1:
                for rep in range(1, event.repetition):
                    temp_year = event.year + rep*(event.frequency == Frequency.YEARLY)
                    temp_month = event.month + rep*(event.frequency == Frequency.MONTHLY)
                    temp_day = event.day + rep*(event.frequency == Frequency.DAILY) + 7*rep*(event.frequency == Frequency.WEEKLY)
                    year, month, day = self.calculate_recurring_events(temp_year, temp_month, temp_day, event.frequency)
                    self.add_item(UserRepeatedEvent(event.item_id, year, month, day, event.name, event.status,
                                                    event.privacy, event.calendar_number))

            elif event.rrule:
                dtstart = event.getDatetime()

                # For infinitely repeated events, we limit them by end of the next year:
                if 'COUNT' not in event.rrule and 'UNTIL' not in event.rrule:
                    until_year = current_year + 1
                    until_month = 12
                    event.rrule += ';UNTIL=' + datetime.datetime(until_year, until_month, 1).strftime('%Y%m%dT%H%M%SZ')

                # Create a list of dates of repeated events:
                try:
                    rule = rrulestr(event.rrule, dtstart=dtstart)
                except ValueError as e:
                    logging.error("Problem occurred with event: '%s'.", event.name)
                    continue
                rset = rruleset()
                rset.rrule(rule)

                if event.exdate:
                    exdates_list = [event.exdate] if not isinstance(event.exdate, list) else event.exdate

                    for exdates in exdates_list:
                        for exdate in exdates.dts:
                            exdate_dt = datetime.datetime.combine(exdate.dt, datetime.time.min, tzinfo=dtstart.tzinfo) if not isinstance(exdate.dt, datetime.datetime) else exdate.dt
                            rset.exdate(exdate_dt)

                # Create an event for each repetition and add to the list:
                for date in list(rset)[1:]:
                    self.add_item(UserRepeatedEvent(event.item_id, date.year, date.month, date.day, event.name,
                                                    event.status, event.privacy, event.calendar_number))

    def calculate_recurring_events(self, year, month, day, frequency):
        """Calculate the date of recurring events so that they occur in the next month or year"""
        new_day = day
        new_month = month
        new_year = year
        skip_days = 0

        # Weekly and daily recurrence:
        if frequency in [Frequency.WEEKLY, Frequency.DAILY]:

            # Calculate how many days and month to skip to next event:
            for i in range(1000):
                if month + i > 12:
                    year = year + 1
                    month = month - 12

                last_day = Calendar(0, self.use_persian_calendar).last_day(year, month+i)
                if day > skip_days + last_day:
                    skip_days += last_day
                    skip_months = i + 1
                else:
                    skip_months = i
                    break
            new_day = day - skip_days
            new_month = month + skip_months
            new_year = year

        # Monthly recurrence:
        if frequency == Frequency.MONTHLY:
            if month > 12:
                new_year = year + (month - 1)//12
                new_month = month - 12*(new_year - year)
        return new_year, new_month, new_day

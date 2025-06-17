"""Module that controls loading data from files and libraries"""

import configparser
import csv
import os
import datetime
import icalendar
import urllib.request
import io
import logging

from pathlib import Path

from calcure.data import *


class LoaderCSV:
    """Load data from CSV files"""

    def create_file(self, filename):
        """Create CSV file"""
        try:
            with open(filename, "w+", encoding="utf-8") as file:
                pass
            return []
        except (FileNotFoundError, NameError) as e_message:
            logging.error("Problem occurred trying to create %s. %s", filename, e_message)
            return []

    def read_file(self, filename):
        """Read CSV file or create new one if it does not exist"""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                lines = csv.reader(file, delimiter = ',')
                return list(lines)
        except IOError: # File does not exist
            # logging.info("Creating %s.", filename)
            return self.create_file(filename)


class TaskLoaderCSV(LoaderCSV):
    """Load tasks from CSV files"""

    def __init__(self, cf):
        self.user_tasks = Tasks()
        self.tasks_file = cf.TASKS_FILE

    @property
    def is_task_format_old(self):
        """Check if the database format is old"""
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            text = f.read()
        return text[0] == '"'

    def load(self):
        """Reads from CSV file"""

        self.user_tasks.delete_all_items()
        lines = self.read_file(self.tasks_file)

        for row in lines:

            # Read task dates:
            if self.is_task_format_old:
                shift = 0
                year = 0
                month = 0
                day = 0
            else:
                shift = 3
                year = int(row[0])
                month = int(row[1])
                day = int(row[2])

            # Read task name and statuses:
            if row[0 + shift].startswith('.'):
                name = row[0 + shift][1:]
                is_private = True
            else:
                name = row[0 + shift]
                is_private = False
            status = Status[row[1 + shift].upper()]
            parent_id = int(row[2 + shift])
            task_id = int(row[3 + shift])
            collapse = (row[4 + shift] == "True")

            stamps = row[(5 + shift):] if len(row) > 5 else []
            timer = Timer(stamps)

            # Add task:
            new_task = Task(task_id, name, status, timer, is_private, parent_id, collapse, year, month, day)
            self.user_tasks.add_item(new_task)
        self.user_tasks.changed = False
        return self.user_tasks

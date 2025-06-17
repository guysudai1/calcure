"""Module that controls saving data files"""

from pathlib import Path

from calcure.data import *


class TaskSaverCSV:
    """Save tasks into CSV files"""

    def __init__(self, user_tasks, cf):
        self.user_tasks = user_tasks
        self.tasks_file = cf.TASKS_FILE

    def save(self):
        """Rewrite CSV file with changed tasks"""
        original_file = self.tasks_file
        dummy_file = Path(f"{self.tasks_file}.bak")
        with open(dummy_file, "w", encoding="utf-8") as f:
            for task in self.user_tasks.all_ordered_tasks:
                year, month, day = task.year, task.month, task.day

                dot = "."
                f.write(f'{year},{month},{day},"{dot*task.privacy}{task.name}",{task.status.name.lower()},{task.parent_id},{task.item_id},{task.collapse}')
                for stamp in task.timer.stamps:
                    f.write(f',{str(stamp)}')
                f.write("\n")
        dummy_file.replace(original_file)
        self.user_tasks.changed = False

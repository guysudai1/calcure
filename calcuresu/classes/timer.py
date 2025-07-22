import time


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

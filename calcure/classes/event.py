import datetime


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

import datetime


class Alarm(object):
    def __init__(self):
        self.name = None
        self.is_active = False
        self.trigger_time = None
        self.trigger_days = None
        self.station = None

    def init(self, name, station):
        self.name = name
        self.is_active = False
        self.trigger_time = datetime.time(hour=8, minute=0, second=0)
        self.trigger_days = [True, True, True, True, True, False, False]
        self.station = station

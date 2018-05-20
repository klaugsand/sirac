import datetime
import logging
import threading

from pydispatch import dispatcher


class Alarm(object):
    def __init__(self):
        self.name = None
        self.is_active = False
        self.trigger_time = None
        self.trigger_days = None
        self.station = None
        # self.next_trigger_day = None
        self.timer = None

    def init(self, name, station):
        self.name = name
        self.is_active = False
        self.trigger_time = datetime.time(hour=8, minute=0, second=0)
        self.trigger_days = [True, True, True, True, True, False, False]
        self.station = station
        
    def trigger(self):
        logging.debug('Alarm.trigger: name - {}, trigger_time - {}, trigger_days - {}'.format(self.name, self.trigger_time, self.trigger_days))
        self.set_next_trigger(False)
        dispatcher.send(signal='ALARM_TRIGGER', sender=self)
    
    '''
    def calc_next_trigger_day(self):
        logging.debug('Alarm.calc_next_trigger_day: trigger_time - {}, trigger_days - {}'.format(self.trigger_time, self.trigger_days))

        timestamp = datetime.datetime.now()
        time_now = datetime.time(hour=timestamp.time().hour, minute=timestamp.time().minute)
        day_now = timestamp.weekday()

        logging.debug('Alarm.calc_next_trigger_day: time_now - {}, day_now - {}'.format(time_now, day_now))

        diff = -1

        if (time_now <= self.trigger_time) and (self.trigger_days[day_now] is True):
            self.next_trigger_day = day_now
        else:
            for index in range(0, 7):
                day = (day_now + 1 + index) % 7
                if self.trigger_days[day] is True:
                    self.next_trigger_day = day
                    break

        logging.debug('Alarm.calc_next_trigger_day: next_trigger_day - {}'.format(self.next_trigger_day))
    '''
    
    def calc_trigger_diff(self, timestamp):
        time_now = datetime.time(hour=timestamp.time().hour, minute=timestamp.time().minute)
        day_now = timestamp.weekday()

        diff = -1
        today = None

        if (time_now <= self.trigger_time) and (self.trigger_days[day_now] is True):
            today = True
            diff = self.trigger_time.hour * 60 + self.trigger_time.minute - time_now.hour * 60 - time_now.minute
        else:
            today = False
            days = 0
            for index in range(0, 7):
                days += 1
                day = (day_now + 1 + index) % 7
                if self.trigger_days[day] is True:
                    break

            day_minutes = (days - 1) * 24 * 60
            dist = day_minutes + self.trigger_time.hour * 60 + self.trigger_time.minute
            rest_of_day = 24 * 60 - time_now.hour * 60 - time_now.minute
            diff = rest_of_day + dist
            
        return diff, today

    def set_next_trigger(self, cancel_existing):
        logging.debug('Alarm.set_next_trigger: trigger_time - {}, trigger_days - {}'.format(self.trigger_time, self.trigger_days))

        timestamp = datetime.datetime.now()
        diff, today = self.calc_trigger_diff(timestamp)

        logging.debug('Alarm.set_next_trigger: today - {}, diff - {}'.format(today, diff))

        trigger_time = timestamp + datetime.timedelta(minutes = diff)
        trigger_time = trigger_time - datetime.timedelta(seconds = trigger_time.second)
        sleep_time = trigger_time - timestamp

        logging.debug('Alarm.set_next_trigger: trigger_time - {}, sleep_time - {}'.format(trigger_time, sleep_time.seconds))
        
        if cancel_existing is True:
            if self.timer is not None:
                logging.debug('Alarm.set_next_trigger: cancelling timer')
                self.timer.cancel()
            
        self.timer = threading.Timer(sleep_time.seconds, self.trigger)
        self.timer.start()

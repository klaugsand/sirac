import io
import jsonpickle
import logging


class Alarms(object):
    def __init__(self):
        self.alarm_file = './data/alarms.json'

        self.alarms = []
        self.alarm_sel = -1

        self.read_alarms_file()
        # self.calc_next_trigger_day()
        self.set_next_trigger(False)

    def read_alarms_file(self):
        try:
            # with io.open(self.alarm_file, 'r', encoding='utf-8') as alarm_file:
            with open(self.alarm_file, 'r') as alarm_file:
                json_str = alarm_file.read()
                obj = jsonpickle.decode(json_str)
                self.alarms = obj
        except EnvironmentError as ex:
            logging.error("Alarms.read_alarms_file: failed to read file %s", self.alarm_file)
        except ValueError as ex:
            logging.error("Alarms.read_alarms_file: failed to parse file %s", self.alarm_file)

    def write_alarms_file(self):
        self.calc_next_trigger_day()
        self.set_next_trigger(True)

        try:
            # with io.open(self.alarm_file, 'w', encoding='utf-8') as alarm_file:
            with open(self.alarm_file, 'w') as alarm_file:
                json_str = jsonpickle.encode(self.alarms)
                alarm_file.write(json_str)
        except EnvironmentError as ex:
            logging.error("Alarms.write_alarms_file: failed to write file %s", self.alarm_file)

    def add_alarm(self, alarm, update_sel=False):
        alarm.calc_next_trigger_day()
        alarm.set_next_trigger(False)
        
        self.alarms.append(alarm)
        self.write_alarms_file()

        if update_sel is True:
            self.set_alarm_sel(self.get_alarm_count() - 1)

    def delete_alarm(self, index):
        if (index >= 0) and (index < len(self.alarms)):
            self.alarms.pop(index)
            self.write_alarms_file()

    def set_alarm_sel(self, index):
        if (index >= 0) and (index < len(self.alarms)):
            self.alarm_sel = index

    def get_alarm_sel(self):
        return self.alarm_sel

    def get_alarms(self):
        return self.alarms

    def get_alarm_count(self):
        return len(self.alarms)

    def get_active_alarms(self):
        active_alarms = []
        for alarm in self.alarms:
            if alarm.is_active is True:
                active_alarms.append(alarm)

        return active_alarms

    '''
    def calc_next_trigger_day(self):
        for alarm in self.alarms:
            alarm.calc_next_trigger_day()
    '''
    
    def set_next_trigger(self, cancel_existing):
        for alarm in self.alarms:
            alarm.set_next_trigger(cancel_existing)

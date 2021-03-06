import datetime
import logging

from event_handler import EventHandler
from controller.controller_base import ControllerBase


class IdleController(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.alarm_model = model.get_model('alarms')
        self.sound_driver = None

        self.show_volume_timestamp = None

    def initialize(self, sound_driver):
        self.sound_driver = sound_driver

    def activate(self):
        # logging.debug('IdleController.activate')

        self.display_driver.set_cursor(0, 0, False)
        self.display_driver.clear()
        self.update_display()

    def time_signal(self, seconds):
        # logging.debug('IdleController.time_signal: seconds - {}'.format(seconds))
        if self.is_active() is True:
            self.update_display()

    def handle_event(self, event):
        consumed = False

        # logging.debug('IdleController.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_LEFT:
            consumed = self.handle_volume(False)
        elif event == EventHandler.EVENT_KEY_RIGHT:
            consumed = self.handle_volume(True)
        elif event == EventHandler.EVENT_KEY_BACK:
            consumed = True

        return consumed

    def handle_volume(self, is_up):
        change = 5
        if is_up is False:
            change = -5

        self.sound_driver.change_volume(change)
        self.show_volume_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=2)

        self.update_display()

        return True

    def get_next_alarm(self, timestamp):
        time_str = ''

        alarm_dist = []
        active_alarms = self.alarm_model.get_active_alarms()
        for alarm in active_alarms:
            diff, today = alarm.calc_trigger_diff(timestamp)

            item = (alarm, diff, today)
            alarm_dist.append(item)

        if len(alarm_dist) > 0:
            alarm_sort = sorted(alarm_dist, key=lambda item: item[1])
            alarm = alarm_sort[0][0]
            time_str = alarm.trigger_time.strftime('%H:%M')
            if alarm_sort[0][2] is False:
                time_str = '+' + time_str

        return time_str

    def update_display(self):
        timestamp = datetime.datetime.now()
        
        clock = timestamp.strftime('%H:%M')
        self.display_driver.write(clock, 0, commit=False)

        alarm = self.get_next_alarm(timestamp)
        self.display_driver.write(alarm, 0, left_adjust=False, clear_row=False)

        if (self.show_volume_timestamp is not None) and (self.show_volume_timestamp >= timestamp):
            volume = 'Volume: {}%'.format(self.sound_driver.get_volume())
            self.display_driver.write(volume, 1)
        else:
            date = timestamp.strftime('%d.%m.%Y')
            self.display_driver.write(date, 1)

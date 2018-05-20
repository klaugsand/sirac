import datetime
import logging

from pydispatch import dispatcher

from event_handler import EventHandler
from controller.controller_base import ControllerBase
from models.alarm import Alarm


class AlarmController(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.alarm_model = model.get_model('alarms')
        self.sound_driver = None

        self.active_alarm = None
        self.snooze_time = None
        
        dispatcher.connect(self.handle_alarm_trigger, signal='ALARM_TRIGGER', sender=dispatcher.Any)

    def initialize(self, sound_driver):
        self.sound_driver = sound_driver
        
    def handle_alarm_trigger(self, sender):
        logging.debug('AlarmController.handle_alarm_trigger: sender - {}'.format(sender))
        self.active_alarm = sender
        self.state_machine.trigger_alarm()

    def activate(self):
        logging.debug('AlarmController.activate')

        if self.active_alarm is not None:
            logging.debug('AlarmController.handle_alarm_trigger: name - {}'.format(self.active_alarm.name))

            self.display_driver.set_cursor(0, 0, False)
            self.display_driver.clear()
            self.update_display()

    def time_signal(self, seconds):
        # logging.debug('AlarmController.time_signal: seconds - {}'.format(seconds))
        if self.is_active() is True:
            self.update_display()
    
    def handle_event(self, event):
        consumed = False

        # logging.debug('AlarmController.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_ENTER:
            consumed = self.set_snooze()
        elif event == EventHandler.EVENT_KEY_BACK:
            consumed = True

        return consumed
        
    def set_snooze(self):
        consumed = True
        
        return consumed

    def update_display(self):
        timestamp = datetime.datetime.now()
        
        clock = timestamp.strftime('%H:%M')
        self.display_driver.write(clock, 0, commit=True)

        # alarm = self.get_next_alarm(timestamp)
        # self.display_driver.write(alarm, 0, left_adjust=False, clear_row=False)

        date = timestamp.strftime('%d.%m.%Y')
        self.display_driver.write(date, 1)

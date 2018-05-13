import logging
import datetime

from event_handler import EventHandler
from controller.controller_base import ControllerBase
from models.alarm import Alarm


class AlarmsController(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.menu_items = None
        self.menu_pos = 0

        self.alarm_model = model.get_model('alarms')
        self.station_model = model.get_model('stations')

        self.build_menu()

    def build_menu(self):
        self.menu_items = []
        menu_item = ['New alarm', self.create_alarm]
        self.menu_items.append(menu_item)

        for alarm in self.alarm_model.get_alarms():
            menu_item = [alarm.name, self.edit_alarm]
            self.menu_items.append(menu_item)

    def time_signal(self, seconds):
        timestamp = datetime.datetime.now()
        time_now = datetime.time(hour=timestamp.time().hour, minute=timestamp.time().minute)
        day_now = timestamp.weekday()
        # logging.debug('AlarmsController.time_signal: time_now: {}, day_now: {}'.format(time_now, day_now))

        active_alarms = self.alarm_model.get_active_alarms()
        for alarm in active_alarms:
            if (time_now == alarm.trigger_time) and (alarm.trigger_days[day_now] is True):
                logging.debug('AlarmsController.time_signal: activate alarm: {}'.format(alarm))

    def create_alarm(self):
        logging.debug('AlarmsController.create_alarm')

        alarm = Alarm()
        alarm_name = 'Alarm ' + str(self.alarm_model.get_alarm_count() + 1)
        alarm_station = self.station_model.get_stations()[0].name
        alarm.init(alarm_name, alarm_station)
        self.alarm_model.add_alarm(alarm, True)

        self.state_machine.new_alarm()

    def edit_alarm(self):
        logging.debug('AlarmsController.edit_alarm')

        self.alarm_model.set_alarm_sel(self.menu_pos - 1)
        self.state_machine.edit_alarm()

    def activate(self):
        logging.debug('AlarmsController.activate')

        self.build_menu()

        if self.menu_pos >= len(self.menu_items):
            self.menu_pos = len(self.menu_items) - 1

        self.update_display()

    def handle_event(self, event):
        consumed = False

        # logging.debug('AlarmsController.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_LEFT:
            consumed = self.update_selection(-1)
        elif event == EventHandler.EVENT_KEY_RIGHT:
            consumed = self.update_selection(1)
        elif event == EventHandler.EVENT_KEY_ENTER:
            selection_method = self.menu_items[self.menu_pos][1]
            selection_method()
            consumed = True

        return consumed

    def update_selection(self, delta):
        self.menu_pos += delta

        if self.menu_pos < 0:
            self.menu_pos = len(self.menu_items) - 1
        elif self.menu_pos >= len(self.menu_items):
            self.menu_pos = 0

        self.update_display(delta > 0)

        return True

    def update_display(self, selection_on_top=True):
        # logging.debug('AlarmsController.update_display: selection_on_top - {}'.format(selection_on_top))

        if selection_on_top is True:
            menu_text = '-> ' + self.menu_items[self.menu_pos][0]
            self.display_driver.write(menu_text, 0)

            next_sel_pos = self.menu_pos + 1
            if next_sel_pos >= len(self.menu_items):
                next_sel_pos = 0
            if next_sel_pos != self.menu_pos:
                menu_text = '   ' + self.menu_items[next_sel_pos][0]
            else:
                menu_text = ''
            self.display_driver.write(menu_text, 1)
        else:
            menu_text = '-> ' + self.menu_items[self.menu_pos][0]
            self.display_driver.write(menu_text, 1)

            prev_sel_pos = self.menu_pos - 1
            if prev_sel_pos < 0:
                prev_sel_pos = len(self.menu_items) - 1
            if prev_sel_pos != self.menu_pos:
                menu_text = '   ' + self.menu_items[prev_sel_pos][0]
            else:
                menu_text = ''
            self.display_driver.write(menu_text, 0)

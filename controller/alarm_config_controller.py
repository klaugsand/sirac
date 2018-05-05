import logging
import datetime

from event_handler import EventHandler
from controller.controller_base import ControllerBase


class AlarmConfigController(ControllerBase):
    STATE_NORMAL = 0
    STATE_SELECT = 1
    STATE_EDIT = 2

    FIELD_NAME = 0
    FIELD_ACTIVE = 1
    FIELD_TIME = 2
    FIELD_DAYS = 3
    FIELD_STATION = 4

    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.current_state = AlarmConfigController.STATE_NORMAL
        self.current_field = AlarmConfigController.FIELD_NAME
        self.current_field_pos = 0
        self.current_field_update = None

        self.active_alarm = None
        self.alarm_model = model.get_model('alarms')
        self.station_model = model.get_model('stations')

    def activate(self):
        # logging.debug('AlarmConfigController.activate')

        self.current_field = AlarmConfigController.FIELD_NAME

        alarms = self.alarm_model.get_alarms()
        index = self.alarm_model.get_alarm_sel()
        self.active_alarm = alarms[index]

        self.update_display()

    def handle_event(self, event):
        consumed = False

        if event == EventHandler.EVENT_KEY_LEFT:
            consumed = self.handle_movement(-1)
        elif event == EventHandler.EVENT_KEY_RIGHT:
            consumed = self.handle_movement(1)
        elif event == EventHandler.EVENT_KEY_ENTER:
            consumed = self.handle_selection()
        elif event == EventHandler.EVENT_KEY_BACK:
            consumed = self.handle_return()

        return consumed

    def handle_movement(self, delta):
        if self.current_state == AlarmConfigController.STATE_NORMAL:
            self.update_selection(delta)
        elif self.current_state == AlarmConfigController.STATE_SELECT:
            self.update_field_position(delta)
        elif self.current_state == AlarmConfigController.STATE_EDIT:
            self.update_field_value(delta)

        return True

    def handle_selection(self):
        if self.current_state == AlarmConfigController.STATE_NORMAL:
            self.set_select_state()
        elif self.current_state == AlarmConfigController.STATE_SELECT:
            self.set_edit_state()
        elif self.current_state == AlarmConfigController.STATE_EDIT:
            self.save_config()

        return True

    def handle_return(self):
        consumed = False

        if self.current_state == AlarmConfigController.STATE_SELECT:
            self.set_normal_state()
            consumed = True
        elif self.current_state == AlarmConfigController.STATE_EDIT:
            self.set_select_state()
            consumed = True

        return consumed

    def set_normal_state(self):
        self.current_state = AlarmConfigController.STATE_NORMAL
        self.update_display()

    def set_select_state(self):
        self.current_state = AlarmConfigController.STATE_SELECT
        self.update_display()

        self.current_field_pos = 0
        self.display_driver.set_cursor(1, self.current_field_pos, True)

    def set_edit_state(self):
        invalid_pos = False

        if self.current_field == AlarmConfigController.FIELD_TIME:
            if self.current_field_pos == 2:
                invalid_pos = True

        if invalid_pos is False:
            self.current_state = AlarmConfigController.STATE_EDIT
            self.current_field_update = self.create_field_value()
            self.update_display()

    def save_config(self):
        if self.current_field == AlarmConfigController.FIELD_NAME:
            self.active_alarm.name = self.current_field_update
        elif self.current_field == AlarmConfigController.FIELD_ACTIVE:
            if self.current_field_update == 'On':
                self.active_alarm.is_active = True
            else:
                self.active_alarm.is_active = False
        elif self.current_field == AlarmConfigController.FIELD_TIME:
            self.active_alarm.trigger_time = datetime.datetime.strptime(self.current_field_update, '%H:%M').time()
        elif self.current_field == AlarmConfigController.FIELD_DAYS:
            for index in range(0, len(self.current_field_update)):
                active = self.current_field_update[index].isupper()
                self.active_alarm.trigger_days[index] = active
        elif self.current_field == AlarmConfigController.FIELD_STATION:
            self.active_alarm.station = self.current_field_update

        self.alarm_model.write_alarms_file()

        self.current_state = AlarmConfigController.STATE_SELECT
        self.update_display()

    def update_selection(self, delta):
        self.current_field += delta

        if self.current_field < AlarmConfigController.FIELD_NAME:
            self.current_field = AlarmConfigController.FIELD_STATION
        elif self.current_field > AlarmConfigController.FIELD_STATION:
            self.current_field = AlarmConfigController.FIELD_NAME

        self.update_display()

    def get_current_field_length(self):
        field_length = 0

        if self.current_field == AlarmConfigController.FIELD_NAME:
            field_length = len(self.active_alarm.name)
        elif self.current_field == AlarmConfigController.FIELD_ACTIVE:
            field_length = 1
        elif self.current_field == AlarmConfigController.FIELD_TIME:
            field_length = 5
        elif self.current_field == AlarmConfigController.FIELD_DAYS:
            field_length = 7
        elif self.current_field == AlarmConfigController.FIELD_STATION:
            field_length = 1

        return field_length

    def update_field_position(self, delta):
        field_length = self.get_current_field_length()

        if self.current_field == AlarmConfigController.FIELD_TIME:
            if self.current_field_pos == 0:
                self.current_field_pos = 3
            else:
                self.current_field_pos = 0
        else:
            self.current_field_pos += delta
            if self.current_field_pos < 0:
                self.current_field_pos = field_length
            elif self.current_field_pos >= field_length:
                self.current_field_pos = 0

        self.display_driver.set_cursor(1, self.current_field_pos, True)

    def update_field_value(self, delta):
        value = self.current_field_update

        if self.current_field == AlarmConfigController.FIELD_NAME:
            change = value[self.current_field_pos:self.current_field_pos + 1]

            valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            index = valid_chars.find(change)
            if index != -1:
                index += delta

                if index < 0:
                    index = len(valid_chars) - 1
                elif index >= len(valid_chars):
                    index = 0

                change = valid_chars[index]
                self.current_field_update = value[:self.current_field_pos] + change + value[self.current_field_pos + 1:]

        elif self.current_field == AlarmConfigController.FIELD_ACTIVE:
            if value == 'On':
                change = 'Off'
            else:
                change = 'On'
            self.current_field_update = change

        elif self.current_field == AlarmConfigController.FIELD_TIME:
            change = value[self.current_field_pos:self.current_field_pos + 2]
            time_part = int(change)
            time_part += delta
            if self.current_field_pos == 0:
                if time_part > 23:
                    time_part = 0
                elif time_part < 0:
                    time_part = 23
            else:
                if time_part > 59:
                    time_part = 0
                elif time_part < 0:
                    time_part = 59

            change = '{:02}'.format(time_part)
            self.current_field_update = value[:self.current_field_pos] + change + value[self.current_field_pos + 2:]

        elif self.current_field == AlarmConfigController.FIELD_DAYS:
            change = value[self.current_field_pos:self.current_field_pos + 1]
            if change.islower():
                change = change.upper()
            else:
                change = change.lower()
            self.current_field_update = value[:self.current_field_pos] + change + value[self.current_field_pos + 1:]

        elif self.current_field == AlarmConfigController.FIELD_STATION:
            index = self.station_model.get_station_index(value)
            max_index = self.station_model.get_station_count() - 1
            index += delta
            if index < 0:
                index = max_index
            elif index > max_index:
                index = 0
            self.current_field_update = self.station_model.get_stations()[index].name

        self.update_display()

    def build_days_string(self):
        day_name = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        day_str = ''
        for day in range(0, 7):
            if self.active_alarm.trigger_days[day] is True:
                day_str += day_name[day]
            else:
                day_str += day_name[day].lower()

        return day_str

    def create_field_heading(self):
        if self.current_field == AlarmConfigController.FIELD_NAME:
            heading = 'Alarm name:'
        elif self.current_field == AlarmConfigController.FIELD_ACTIVE:
            heading = 'Alarm activated:'
        elif self.current_field == AlarmConfigController.FIELD_TIME:
            heading = 'Alarm time:'
        elif self.current_field == AlarmConfigController.FIELD_DAYS:
            heading = 'Alarm days:'
        elif self.current_field == AlarmConfigController.FIELD_STATION:
            heading = 'Station:'

        return heading

    def create_field_value(self):
        if self.current_field == AlarmConfigController.FIELD_NAME:
            value = self.active_alarm.name
        elif self.current_field == AlarmConfigController.FIELD_ACTIVE:
            if self.active_alarm.is_active is True:
                value = 'On'
            else:
                value = 'Off'
        elif self.current_field == AlarmConfigController.FIELD_TIME:
            value = self.active_alarm.trigger_time.strftime('%H:%M')
        elif self.current_field == AlarmConfigController.FIELD_DAYS:
            value = self.build_days_string()
        elif self.current_field == AlarmConfigController.FIELD_STATION:
            value = self.active_alarm.station

        return value

    def create_normal_display(self):
        line1 = self.create_field_heading()
        line2 = self.create_field_value()

        return line1, line2

    def create_select_display(self):
        line1 = self.create_field_heading()
        line2 = self.create_field_value()

        return line1, line2

    def create_edit_display(self):
        line1 = self.create_field_heading()
        line2 = self.current_field_update

        return line1, line2

    def update_display(self):
        if self.current_state == AlarmConfigController.STATE_NORMAL:
            line1, line2 = self.create_normal_display()
        elif self.current_state == AlarmConfigController.STATE_SELECT:
            line1, line2 = self.create_select_display()
        elif self.current_state == AlarmConfigController.STATE_EDIT:
            line1, line2 = self.create_edit_display()

        self.display_driver.write(line1, 0)
        self.display_driver.write(line2, 1)

import logging

from event_handler import EventHandler
from sound_driver import SoundDriver
from controller.controller_base import ControllerBase


class StationsController(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.menu_pos = 0
        self.uri_playing = None

        self.station_model = model.get_model('stations')
        self.sound_driver = None

    def initialize(self, sound_driver):
        self.sound_driver = sound_driver

    def activate(self):
        logging.debug('StationsController.activate')

        self.update_display()

    def handle_event(self, event):
        consumed = False

        # logging.debug('StationsController.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_LEFT:
            consumed = self.update_selection(-1)
        elif event == EventHandler.EVENT_KEY_RIGHT:
            consumed = self.update_selection(1)
        elif event == EventHandler.EVENT_KEY_ENTER:
            consumed = self.handle_selection()

        return consumed

    def update_selection(self, delta):
        self.menu_pos += delta

        max_sel = self.station_model.get_station_count()

        if self.menu_pos < 0:
            self.menu_pos = max_sel - 1
        elif self.menu_pos >= max_sel:
            self.menu_pos = 0

        self.update_display(delta > 0)

        return True

    def handle_selection(self):
        if self.uri_playing is None:
            stations = self.station_model.get_stations()
            self.uri_playing = stations[self.menu_pos].uri

            logging.debug('StationsController.handle_selection: start playback - {}'.format(self.uri_playing))
            
            self.sound_driver.play(self.uri_playing)
        else:
            self.uri_playing = None
            
            logging.debug('StationsController.handle_selection: stop playback')
            
            self.sound_driver.stop()

        return True

    def update_display(self, selection_on_top=True):
        # logging.debug('StationsController.update_display: selection_on_top - {}'.format(selection_on_top))

        stations = self.station_model.get_stations()

        if selection_on_top is True:
            menu_text = '-> ' + stations[self.menu_pos].name
            self.display_driver.write(menu_text, 0)

            next_sel_pos = self.menu_pos + 1
            if next_sel_pos >= len(stations):
                next_sel_pos = 0
            if next_sel_pos != self.menu_pos:
                menu_text = '   ' + stations[next_sel_pos].name
            else:
                menu_text = ''
            self.display_driver.write(menu_text, 1)
        else:
            menu_text = '-> ' + stations[self.menu_pos].name
            self.display_driver.write(menu_text, 1)

            prev_sel_pos = self.menu_pos - 1
            if prev_sel_pos < 0:
                prev_sel_pos = len(stations) - 1
            if prev_sel_pos != self.menu_pos:
                menu_text = '   ' + stations[prev_sel_pos].name
            else:
                menu_text = ''
            self.display_driver.write(menu_text, 0)

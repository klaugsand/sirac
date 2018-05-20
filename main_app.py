import time
import logging
import os

from transitions import Machine, State

from display_driver import DisplayDriver
from display_driver_pcf8574 import DisplayDriverPCF8574
from sound_driver import SoundDriver
from event_handler import EventHandler
from controller.idle_controller import IdleController
from controller.alarm_controller import AlarmController
from controller.main_menu_controller import MainMenuController
from controller.alarms_controller import AlarmsController
from controller.stations_controller import StationsController
from controller.config_controller import ConfigController
from controller.alarm_modify_controller import AlarmModifyController
from controller.alarm_config_controller import AlarmConfigController

from models.model_container import ModelContainer
from models.alarms import Alarms
from models.stations import Stations

from models.station import Station


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S')


class MainApp(object):
    def __init__(self):
        self.native_mode = False
        node_name = os.uname()[1]
        if node_name == 'raspberrypi':
            self.native_mode = True
            
        logging.debug('MainApp.__init__: native_mode {}'.format(self.native_mode))

        if self.native_mode is True:
            self.display = DisplayDriverPCF8574()
        else:
            self.display = DisplayDriver(2, 16, debug_mode=False)
        self.sound = SoundDriver()

        self.model = ModelContainer()
        self.controllers = {}

        self.state_machine = None
        self.event_handler = None

    def init_state_machine(self):
        states = ['idle', 'alarm', 'main_menu', 'alarms', 'stations', 'config', 'alarm_modify', 'alarm_config']

        transitions = [
            {'trigger': 'trigger_alarm', 'source': '*', 'dest': 'alarm'},

            # {'trigger': 'button_right', 'source': 'idle', 'dest': 'main_menu'},
            # {'trigger': 'button_left', 'source': 'idle', 'dest': 'main_menu'},
            {'trigger': 'button_enter', 'source': 'idle', 'dest': 'main_menu'},

            {'trigger': 'button_back', 'source': 'alarm', 'dest': 'idle'},

            {'trigger': 'button_back', 'source': 'main_menu', 'dest': 'idle'},
            {'trigger': 'select_alarms', 'source': 'main_menu', 'dest': 'alarms'},
            {'trigger': 'select_stations', 'source': 'main_menu', 'dest': 'stations'},
            {'trigger': 'select_config', 'source': 'main_menu', 'dest': 'config'},

            {'trigger': 'button_back', 'source': 'alarms', 'dest': 'main_menu'},
            {'trigger': 'edit_alarm', 'source': 'alarms', 'dest': 'alarm_modify'},
            {'trigger': 'new_alarm', 'source': 'alarms', 'dest': 'alarm_config'},

            {'trigger': 'button_back', 'source': 'alarm_modify', 'dest': 'alarms'},
            {'trigger': 'edit_alarm', 'source': 'alarm_modify', 'dest': 'alarm_config'},
            {'trigger': 'delete_alarm', 'source': 'alarm_modify', 'dest': 'alarms'},

            {'trigger': 'button_back', 'source': 'alarm_config', 'dest': 'alarms'},

            {'trigger': 'button_back', 'source': 'stations', 'dest': 'main_menu'},

            {'trigger': 'button_back', 'source': 'config', 'dest': 'main_menu'}
        ]

        logging.getLogger('transitions').setLevel(logging.ERROR)

        self.state_machine = Machine(states=states, transitions=transitions, initial='idle',
                                     # before_state_change=self.before_state_change,
                                     after_state_change=self.after_state_change)

    def init_models(self):
        alarms = Alarms()
        self.model.add_model('alarms', alarms)

        stations = Stations()
        self.model.add_model('stations', stations)

        # self.add_default_stations(stations)

    def add_default_stations(self, stations):
        self.add_station(stations, 'NRK P13', 'http://lyd.nrk.no/nrk_radio_p13_mp3_h')
        self.add_station(stations, 'P5 Hits', 'http://stream.p4.no/p5oslo_mp3_hq')
        self.add_station(stations, 'P4 Lyden av Norge', 'http://stream.p4.no/p4_mp3_hq')
        self.add_station(stations, 'P7 Klem', 'http://stream.p4.no/p7_mp3_hq')
        self.add_station(stations, 'Radio Norge', 'http://tx-bauerno.sharp-stream.com/http_live.php?i=radionorge_no_hq')
        self.add_station(stations, 'Radio Topp 40', 'http://tx-bauerno.sharp-stream.com/http_live.php?i=top40_no_hq')

    def add_station(self, stations, name, uri):
        station = Station()
        station.init(name, uri)
        stations.add_station(station)

    def init_controllers(self):
        self.controllers['idle'] = IdleController('idle', self.state_machine, self.display, self.model)
        self.controllers['alarm'] = AlarmController('alarm', self.state_machine, self.display, self.model)
        self.controllers['main_menu'] = MainMenuController('main_menu', self.state_machine, self.display, self.model)
        self.controllers['alarms'] = AlarmsController('alarms', self.state_machine, self.display, self.model)
        self.controllers['stations'] = StationsController('stations', self.state_machine, self.display, self.model)
        self.controllers['config'] = ConfigController('config', self.state_machine, self.display, self.model)
        self.controllers['alarm_modify'] = AlarmModifyController('alarm_modify', self.state_machine, self.display, self.model)
        self.controllers['alarm_config'] = AlarmConfigController('alarm_config', self.state_machine, self.display, self.model)

        self.controllers['idle'].initialize(self.sound)
        self.controllers['alarm'].initialize(self.sound)
        self.controllers['stations'].initialize(self.sound)

        self.controllers['idle'].activate()

    def before_state_change(self):
        # logging.debug('MainApp.before_state_change: state {}'.format(self.state_machine.state))
        pass

    def after_state_change(self):
        # logging.debug('MainApp.after_state_change: state - {}'.format(self.state_machine.state))

        state_name = self.state_machine.state
        if state_name in self.controllers:
            controller = self.controllers[state_name]
            self.event_handler.set_receiver(controller)
            controller.activate()
        else:
            logging.error('unknown state controller - {}'.format(state_name))

    def handle_event(self, event):
        # logging.debug('MainApp.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_LEFT:
            self.state_machine.button_left()
        elif event == EventHandler.EVENT_KEY_RIGHT:
            self.state_machine.button_right()
        elif event == EventHandler.EVENT_KEY_BACK:
            self.state_machine.button_back()
        elif event == EventHandler.EVENT_KEY_ENTER:
            self.state_machine.button_enter()

    def send_time_signal(self):
        seconds = time.time()
        for key in self.controllers:
            controller = self.controllers[key]
            controller.time_signal(seconds)

    def run(self):
        self.init_models()
        self.init_state_machine()
        self.init_controllers()

        self.event_handler = EventHandler(name='EventHandler', native_mode=self.native_mode)
        self.event_handler.initialize(self, self.controllers['idle'])
        self.event_handler.start()

        while True:
            # logging.debug('MainApp.run: state - {}'.format(self.state_machine.state))
            time.sleep(1)
            self.send_time_signal()


if __name__ == "__main__":
    app = MainApp()
    app.run()

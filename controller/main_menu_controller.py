import logging

from controller.controller_menu import ControllerMenu


class MainMenuController(ControllerMenu):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerMenu.__init__(self, state_name, state_machine, display_driver, model)

        self.add_menu_item('Alarms', self.state_machine.select_alarms)
        self.add_menu_item('Stations', self.state_machine.select_stations)
        self.add_menu_item('Config', self.state_machine.select_config)

    def activate(self):
        # logging.debug('MainMenuController.activate')
        self.update_display()

    def handle_event(self, event):
        consumed = False

        # logging.debug('MainMenuController.handle_event: event - {}'.format(event))

        consumed = self.navigate_menu(event)

        return consumed

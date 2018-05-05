import logging

from event_handler import EventHandler
from controller.controller_base import ControllerBase


class ConfigController(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

    def activate(self):
        logging.debug('ConfigController.activate')
        self.update_display()

    def handle_event(self, event):
        consumed = False

        # logging.debug('ConfigController.handle_event: event - {}'.format(event))

        if event == EventHandler.EVENT_KEY_LEFT:
            consumed = True
        elif event == EventHandler.EVENT_KEY_RIGHT:
            consumed = True
        elif event == EventHandler.EVENT_KEY_ENTER:
            consumed = True

        return consumed

    def update_display(self):
        self.display_driver.clear()

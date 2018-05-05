import logging

from controller.controller_menu import ControllerMenu


class AlarmModifyController(ControllerMenu):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerMenu.__init__(self, state_name, state_machine, display_driver, model)

        self.add_menu_item('Edit alarm', self.state_machine.edit_alarm)
        self.add_menu_item('Delete alarm', self.delete_alarm)

        self.model = model.get_model('alarms')

    def activate(self):
        # logging.debug('AlarmModifyController.activate')

        self.menu_pos = 0
        self.update_display()

    def delete_alarm(self):
        index = self.model.get_alarm_sel()
        self.model.delete_alarm(index)

        self.state_machine.delete_alarm()

    def handle_event(self, event):
        consumed = False

        # logging.debug('AlarmModifyController.handle_event: event - {}'.format(event))

        consumed = self.navigate_menu(event)

        return consumed

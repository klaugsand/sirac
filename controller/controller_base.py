class ControllerBase(object):
    def __init__(self, state_name, state_machine, display_driver, model):
        self.state_name = state_name
        self.state_machine = state_machine
        self.display_driver = display_driver
        self.alarm_model = model

    def is_active(self):
        active = False

        current_state_name = self.state_machine.state
        if current_state_name == self.state_name:
            active = True

        return active

    def time_signal(self, seconds):
        pass

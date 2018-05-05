import logging

from event_handler import EventHandler
from controller.controller_base import ControllerBase


class ControllerMenu(ControllerBase):
    def __init__(self, state_name, state_machine, display_driver, model):
        ControllerBase.__init__(self, state_name, state_machine, display_driver, model)

        self.menu_items = []
        self.menu_pos = 0

    def add_menu_item(self, text, selection_method):
        self.menu_items.append([text, selection_method])

    def navigate_menu(self, event):
        consumed = False

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
        if selection_on_top is True:
            menu_text = '-> ' + self.menu_items[self.menu_pos][0]
            self.display_driver.write(menu_text, 0)

            next_sel_pos = self.menu_pos + 1
            if next_sel_pos >= len(self.menu_items):
                next_sel_pos = 0
            menu_text = '   ' + self.menu_items[next_sel_pos][0]
            self.display_driver.write(menu_text, 1)
        else:
            menu_text = '-> ' + self.menu_items[self.menu_pos][0]
            self.display_driver.write(menu_text, 1)

            prev_sel_pos = self.menu_pos - 1
            if prev_sel_pos < 0:
                prev_sel_pos = len(self.menu_items) - 1
            menu_text = '   ' + self.menu_items[prev_sel_pos][0]
            self.display_driver.write(menu_text, 0)

import threading
import logging
import sys
import select


class EventHandler(threading.Thread):
    EVENT_KEY_ENTER = 1
    EVENT_KEY_BACK = 2
    EVENT_KEY_LEFT = 3
    EVENT_KEY_RIGHT = 4

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)

        self.args = args
        self.kwargs = kwargs

        self.parent = None
        self.receiver = None

        self.exit_event = threading.Event()

    def initialize(self, parent, receiver):
        logging.debug('EventHandler.initialize: starting')
        self.parent = parent
        self.set_receiver(receiver)

    def set_receiver(self, receiver):
        self.receiver = receiver

    def check_for_event(self):
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                logging.debug('EventHandler.check_for_event: keypress {}'.format(line[0]))

                event = None
                if line[0] == 'b':
                    event = EventHandler.EVENT_KEY_BACK
                elif line[0] == 'e':
                    event = EventHandler.EVENT_KEY_ENTER
                elif line[0] == 'l':
                    event = EventHandler.EVENT_KEY_LEFT
                elif line[0] == 'r':
                    event = EventHandler.EVENT_KEY_RIGHT

                consumed = self.receiver.handle_event(event)
                if consumed is False:
                    self.parent.handle_event(event)

    def run(self):
        logging.debug('EventHandler.run: starting')

        while not self.exit_event.isSet():
            is_set = self.exit_event.isSet()
            if is_set:
                logging.info('EventHandler.run: stopping...')
            else:
                self.check_for_event()

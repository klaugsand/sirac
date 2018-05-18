import threading
import logging
import sys
import select
import queue

import RPi.GPIO as GPIO

from time import sleep


class EventHandler(threading.Thread):
    EVENT_KEY_ENTER = 1
    EVENT_KEY_BACK = 2
    EVENT_KEY_LEFT = 3
    EVENT_KEY_RIGHT = 4
    EVENT_KEY_EXIT = 5
    
    Pin_Enc_A = 23
    Pin_Enc_B = 24
    Pin_Enc_Button = 4
    Pin_Right_Button = 5
    Pin_Left_Button = 6


    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, native_mode=False):
        threading.Thread.__init__(self, group=group, target=target, name=name)

        self.args = args
        self.kwargs = kwargs

        self.parent = None
        self.receiver = None

        self.native_mode = native_mode
        logging.debug('EventHandler.__init__: native_mode {}'.format(self.native_mode))
        
        self.curr_rotary_a = 1
        self.curr_rotary_b = 1
        
        self.last_event = None
        self.last_event_time = None
        
        if self.native_mode is True:
            self.init_native()

        self.event_queue = queue.Queue()
        self.exit_event = threading.Event()
        
    def rotary_interrupt(self, channel):
        switch_a = GPIO.input(EventHandler.Pin_Enc_A)
        switch_b = GPIO.input(EventHandler.Pin_Enc_B)

        if (self.curr_rotary_a == switch_a) and (self.curr_rotary_b == switch_b):
            return

        self.curr_rotary_a = switch_a
        self.curr_rotary_b = switch_b
        
        event = None

        if (switch_a and switch_b):
            if channel == EventHandler.Pin_Enc_B:
                logging.debug('Turn right')
                event = EventHandler.EVENT_KEY_RIGHT
            else:
                logging.debug('Turn left')
                event = EventHandler.EVENT_KEY_LEFT
                
        if event is not None:
            self.event_queue.put(event)

    def button_callback(self, channel):
        event = None
        
        if channel == EventHandler.Pin_Enc_Button:
            if GPIO.input(EventHandler.Pin_Enc_Button) == GPIO.LOW:
                logging.debug('Rotary button pressed')
                event = EventHandler.EVENT_KEY_ENTER
        elif channel == EventHandler.Pin_Left_Button:
            if GPIO.input(EventHandler.Pin_Left_Button) == GPIO.LOW:
                logging.debug('Back button pressed')
                event = EventHandler.EVENT_KEY_BACK
        elif channel == EventHandler.Pin_Right_Button:
            if GPIO.input(EventHandler.Pin_Right_Button) == GPIO.LOW:
                logging.debug('Exit button pressed')
                event = EventHandler.EVENT_KEY_EXIT
                
        if event is not None:
            self.event_queue.put(event)

    def init_native(self):
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(EventHandler.Pin_Enc_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(EventHandler.Pin_Enc_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(EventHandler.Pin_Enc_A, GPIO.RISING, callback=self.rotary_interrupt)
        GPIO.add_event_detect(EventHandler.Pin_Enc_B, GPIO.RISING, callback=self.rotary_interrupt)

        GPIO.setup(EventHandler.Pin_Enc_Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(EventHandler.Pin_Enc_Button, GPIO.BOTH, callback=self.button_callback)

        GPIO.setup(EventHandler.Pin_Left_Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(EventHandler.Pin_Left_Button, GPIO.BOTH, callback=self.button_callback)

        GPIO.setup(EventHandler.Pin_Right_Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(EventHandler.Pin_Right_Button, GPIO.BOTH, callback=self.button_callback)

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
                if self.native_mode is True:
                    # sleep(0.1)
                    event = self.event_queue.get()
                    logging.debug('EventHandler.run: processing event {}'.format(event))
                    consumed = self.receiver.handle_event(event)
                    if consumed is False:
                        self.parent.handle_event(event)
                else:
                    self.check_for_event()

import logging
import threading

from RPLCD.i2c import CharLCD


class DisplayDriverPCF8574(object):
    def __init__(self):
        self.row_count = 2
        self.col_count = 16
        
        self.frame_buffer = None
        self.update_buffer = None
        self.change_set = None
        
        self.update_lock = threading.RLock()
        
        self.lcd = None

        self.cursor_data = [0, 0, False]
        self.cursor_update = [0, 0, False]

        self._init_lcd()
        self._setup()

    def _init_lcd(self):
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.backlight_enabled = False

    def _setup(self):
        self.frame_buffer = []
        self.update_buffer = []
        for index in range(0, self.row_count):
            self.frame_buffer.append(bytearray(' ' * self.col_count, 'ascii'))
            self.update_buffer.append(bytearray(' ' * self.col_count, 'ascii'))

    def get_rows(self):
        return self.row_count

    def get_cols(self):
        return self.col_count

    def clear(self, row=None):
        self.update_lock.acquire()

        if row is None:
            for index in range(0, self.row_count):
                self.write('', index, clear_row=True)
        else:
            if row < self.row_count:
                self.write('', row, clear_row=True)

        self.update_lock.release()

    def write(self, text, row, left_adjust=True, clear_row=True, commit=True):
        self.update_lock.acquire()
        
        if row < self.row_count:
            if clear_row is True:
                self.update_buffer[row] = bytearray(' ' * self.col_count, 'ascii')

            text = text.encode('ascii', 'replace')

            if len(text) > self.col_count:
                text = text[:self.col_count]

            if left_adjust is True:
                start = 0
            else:
                start = self.col_count - len(text)

            stop = start + len(text)
            pos = 0
            for index in range(start, stop):
                self.update_buffer[row][index] = text[pos]
                pos += 1

            if commit is True:
                self._update_display()
                
        self.update_lock.release()

    def set_cursor(self, row, col, visible):
        self.update_lock.acquire()

        self.cursor_update = []
        self.cursor_update.append(row)
        self.cursor_update.append(col)
        self.cursor_update.append(visible)

        self._update_cursor()

        self.update_lock.release()

    def _is_cursor_update(self):
        update = False

        if (self.cursor_data[0] != self.cursor_update[0]) or \
           (self.cursor_data[1] != self.cursor_update[1]) or \
           (self.cursor_data[2] != self.cursor_update[2]):
            update = True

        return update

    def _update_cursor(self):
        if self._is_cursor_update() is True:
            # cursor_text = ' - r:{}, c:{}, v:{}'.format(self.cursor_update[0], self.cursor_update[1], self.cursor_update[2])
            self.cursor_data = self.cursor_update
            
            self.lcd.cursor_pos = (self.cursor_data[0], self.cursor_data[1])
            if self.cursor_data[2] is True:
                self.lcd.cursor_mode = 'line'
            else:
                self.lcd.cursor_mode = 'hide'

    def _update_display(self):
        self._create_change_set()
        self.lcd.backlight_enabled = True
        self._show_display()

    def _is_cell_changed(self, row, col):
        is_changed = False

        for item in self.change_set:
            if (item[0] == row) and (item[1] == col):
                is_changed = True
                break

        return is_changed

    def _create_change_set(self):
        self.change_set = []
        for row in range(0, self.row_count):
            for col in range(0, self.col_count):
                if (self.frame_buffer is None) or (self.update_buffer[row][col] != self.frame_buffer[row][col]):
                    item = (row, col)
                    self.change_set.append(item)

    def _show_display(self):
        if len(self.change_set) > 0:
            for row in range(0, self.row_count):
                for col in range(0, self.col_count):
                    if self._is_cell_changed(row, col) is True:
                        self.frame_buffer[row][col] = self.update_buffer[row][col]

                        self.lcd.cursor_pos = (row, col)
                        
                        line_str = str(self.update_buffer[row], 'ascii')
                        display_char = line_str[col]
                        # logging.debug('row: {}, col: {}, char: {}, str: {}'.format(row, col, display_char, line_str))
                        
                        self.lcd.write_string(display_char)

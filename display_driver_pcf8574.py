import logging

from RPLCD.i2c import CharLCD


class DisplayDriverPCF8574(object):
    def __init__(self):
        # self.row_count = rows
        self.row_count = 2
        # self.col_count = cols
        self.col_count = 16
        # self.debug_mode = debug_mode
        
        # logging.debug('DisplayDriverPCF8574.__init__: native_mode {}'.format(self.native_mode))

        self.frame_buffer = None
        self.update_buffer = None
        self.change_set = None
        
        self.lcd = None

        self.cursor_data = [0, 0, False]
        self.cursor_update = [0, 0, False]

        self.init_lcd()
        self.setup()

    def init_lcd(self):
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.backlight_enabled = False

    def setup(self):
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
        if row is None:
            for index in range(0, self.row_count):
                self.write('', index, clear_row=True)
        else:
            if row < self.row_count:
                self.write('', row, clear_row=True)

    def write(self, text, row, left_adjust=True, clear_row=True, commit=True):
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
                self.update_display()

    def set_cursor(self, row, col, visible):
        self.cursor_update = []
        self.cursor_update.append(row)
        self.cursor_update.append(col)
        self.cursor_update.append(visible)

        self.update_cursor()

    def is_cursor_update(self):
        update = False

        if (self.cursor_data[0] != self.cursor_update[0]) or \
           (self.cursor_data[1] != self.cursor_update[1]) or \
           (self.cursor_data[2] != self.cursor_update[2]):
            update = True

        return update

    def update_cursor(self):
        if self.is_cursor_update() is True:
            # cursor_text = ' - r:{}, c:{}, v:{}'.format(self.cursor_update[0], self.cursor_update[1], self.cursor_update[2])
            self.cursor_data = self.cursor_update
            
            self.lcd.cursor_pos = (self.cursor_data[0], self.cursor_data[1])
            if self.cursor_data[2] is True:
                self.lcd.cursor_mode = line
            else:
                self.lcd.cursor_mode = hide

    def update_display(self):
        self.create_change_set()
        self.lcd.backlight_enabled = True
        self.show_display()

    def is_cell_changed(self, row, col):
        is_changed = False

        for item in self.change_set:
            if (item[0] == row) and (item[1] == col):
                is_changed = True
                break

        return is_changed

    def create_change_set(self):
        self.change_set = []
        for row in range(0, self.row_count):
            for col in range(0, self.col_count):
                if (self.frame_buffer is None) or (self.update_buffer[row][col] != self.frame_buffer[row][col]):
                    item = (row, col)
                    self.change_set.append(item)

    def show_display(self):
        if len(self.change_set) > 0:
            for row in range(0, self.row_count):
                for col in range(0, self.col_count):
                    if self.is_cell_changed(row, col) is True:
                        self.frame_buffer[row][col] = self.update_buffer[row][col]

                        self.lcd.cursor_pos = (row, col)
                        
                        line_str = str(self.update_buffer[row], 'ascii')
                        display_char = line_str[col]
                        # logging.debug('row: {}, col: {}, char: {}, str: {}'.format(row, col, display_char, line_str))
                        
                        self.lcd.write_string(display_char)

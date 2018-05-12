import logging

# import term
from RPLCD.i2c import CharLCD


class DisplayDriver(object):
    def __init__(self, rows, cols, debug_mode=False, native_mode=False):
        self.row_count = rows
        self.col_count = cols
        self.debug_mode = debug_mode
        self.native_mode = native_mode
        
        logging.debug('DisplayDriver.__init__: native_mode {}'.format(self.native_mode))

        self.change_set = []

        self.frame_buffer = None
        self.update_buffer = None
        
        self.lcd = None

        self.cursor_data = [0, 0, False]
        self.cursor_update = [0, 0, False]

        self.setup()

    def setup(self):
        self.frame_buffer = []
        self.update_buffer = []
        for index in range(0, self.row_count):
            self.frame_buffer.append(bytearray(' ' * self.col_count, 'utf8'))
            self.update_buffer.append(bytearray(' ' * self.col_count, 'utf8'))

        if self.debug_mode is False:
            if self.native_mode is True:
                self.init_lcd()
			# else:
            #    term.clear()
            
    def init_lcd(self):
        self.lcd = CharLCD('PCF8574', 0x27)
        self.lcd.clear()
        self.lcd.backlight_enabled = False

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

    def write(self, text, row, left_adjust=True, clear_row=True):
        if row < self.row_count:
            if clear_row is True:
                self.update_buffer[row] = bytearray(' ' * self.col_count, 'utf8')
            else:
                self.update_buffer[row] = bytearray(self.frame_buffer[row])

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

            self.update_display()

    def set_cursor(self, row, col, visible):
        self.cursor_update = []
        self.cursor_update.append(row)
        self.cursor_update.append(col)
        self.cursor_update.append(visible)

        self.update_cursor()

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

    def is_cursor_update(self):
        update = False

        if (self.cursor_data[0] != self.cursor_update[0]) or \
           (self.cursor_data[1] != self.cursor_update[1]) or \
           (self.cursor_data[2] != self.cursor_update[2]):
            update = True

        return update

    def update_cursor(self):
        if self.debug_mode is True:
            self.show_debug_display()
        else:
            self.show_normal_display()

    def update_display(self):
        self.create_change_set()

        if self.debug_mode is True:
            self.show_debug_display()
        else:
            self.show_normal_display()

    def show_normal_display(self):
        if len(self.change_set) > 0:
            for row in range(0, self.row_count):
                for col in range(0, self.col_count):
                    if self.is_cell_changed(row, col) is True:
                        self.frame_buffer[row][col] = self.update_buffer[row][col]

                # term.pos(row + 1, 1)
                self.lcd.cursor_pos = (row, 0)
                
                line_str = str(self.update_buffer[row])
                
                # term.write(line_str)
                self.lcd.write_string(line_str)

        if self.is_cursor_update() is True:
            cursor_text = ' - r:{}, c:{}, v:{}'.format(self.cursor_update[0], self.cursor_update[1], self.cursor_update[2])
            self.cursor_data = self.cursor_update
            term.write(cursor_text)

    def show_debug_display(self):
        print('{}'.format('-' * self.col_count))

        for row in range(0, self.row_count):
            change_str = ''
            for col in range(0, self.col_count):
                if self.is_cell_changed(row, col) is True:
                    self.frame_buffer[row][col] = self.update_buffer[row][col]
                    change_str += '*'
                else:
                    change_str += ' '

            print('{}'.format(change_str))

            line_str = str(self.update_buffer[row])
            print('{}'.format(line_str))

        print('{}'.format('-' * self.col_count))

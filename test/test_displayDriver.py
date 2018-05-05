from unittest import TestCase
from display_driver import DisplayDriver


class TestDisplayDriver(TestCase):
    def setUp(self):
        self.disp = DisplayDriver(2, 16, debug_mode=False)

    def tearDown(self):
        pass

    def test_clear(self):
        self.disp.setup()
        self.assertEqual(self.disp.frame_buffer[0], ' ' * 16)
        self.assertEqual(self.disp.frame_buffer[1], ' ' * 16)

    def test_write_upper_left(self):
        self.disp.write('kjetil', 0)
        self.assertEqual(self.disp.frame_buffer[0], 'kjetil          ')

    def test_write_upper_right(self):
        self.disp.write('kjetil', 0, left_adjust=False)
        self.assertEqual(self.disp.frame_buffer[0], '          kjetil')

    def test_write_lower_left(self):
        self.disp.write('kjetil', 1)
        self.assertEqual(self.disp.frame_buffer[1], 'kjetil          ')

    def test_write_lower_right(self):
        self.disp.write('kjetil', 1, left_adjust=False)
        self.assertEqual(self.disp.frame_buffer[1], '          kjetil')

    def test_write_clear(self):
        self.disp.write('kjetil', 0)
        self.disp.write('42', 0, left_adjust=False)
        self.assertEqual(self.disp.frame_buffer[0], '              42')

    def test_write_no_clear(self):
        self.disp.write('kjetil', 0)
        self.disp.write('42', 0, left_adjust=False, clear_row=False)
        self.assertEqual(self.disp.frame_buffer[0], 'kjetil        42')

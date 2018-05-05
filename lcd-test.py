import time
from RPLCD.i2c import CharLCD


lcd = CharLCD('PCF8574', 0x27)

lcd.clear()

lcd.backlight_enabled = False
time.sleep(1)
lcd.backlight_enabled = True
time.sleep(1)

lcd.write_string('Hello world')
time.sleep(5)

lcd.clear()
lcd.close()

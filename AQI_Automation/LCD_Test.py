from RPLCD import CharLCD
from RPi import GPIO

GPIO.setwarnings(False)

GPIO.setup(26, GPIO

# lcd = CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23])
lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=GPIO26, pin_e=GPIO19, pins_data=[GPIO23, GPIO22, GPIO21, GPIO14])

lcd.write_string(u'Hello world!')
lcd.cursor_pos = (1, 0)
lcd.write_string('testing')
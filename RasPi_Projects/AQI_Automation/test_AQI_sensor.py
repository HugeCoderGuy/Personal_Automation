import time
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.uart import PM25_UART
import serial

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
reset_pin = DigitalInOut(board.D0)
reset_pin.direction = Direction.OUTPUT
reset_pin.value = False


uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
# Connect to a PM2.5 sensor over UART
pm25 = PM25_UART(uart, reset_pin)


print("Found PM2.5 sensor, reading data...")

while True:


    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")
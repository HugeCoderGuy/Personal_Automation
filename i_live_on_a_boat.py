# pylint: disable=unused-import
import requests
from api_key import api_key
import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.uart import PM25_UART
import serial
from RPLCD import CharLCD


def aqi_api(city_or_station_name):
    # Input: string of city or station idx followed by @ (ex. '@3894')
    # Output: (aqi, pm25)
    city = city_or_station_name
    url = 'http://api.waqi.info/feed/' + city + '/?token=' + api_key

    r = requests.get(url)
    data = r.json()['data']
    aqi = data['aqi']
    iaqi = data['iaqi']
    dew = iaqi.get('dew','Nil')
    no2 = iaqi.get('no2','Nil')
    o3 = iaqi.get('o3','Nil')
    so2 = iaqi.get('so2','Nil')
    pm10 = iaqi.get('pm10','Nil')
    pm25 = iaqi.get('pm25','Nil')
    pollen = iaqi.get('pol','Nil')

    print(f'{city} AQI :',aqi,'\n')
    return aqi, pm25['v']

def aqiSensor():
    reset_pin = None
    # If you have a GPIO, its not a bad idea to connect it to the RESET pin
    reset_pin = DigitalInOut(board.G0)
    reset_pin.direction = Direction.OUTPUT
    reset_pin.value = False


    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
    # Connect to a PM2.5 sensor over UART
    pm25 = PM25_UART(uart, reset_pin)


    print("Found PM2.5 sensor, reading data...")

    time.sleep(1)

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
    return str("PM 1.0: %d\tPM2.5: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"]))

def LCD_Setup():
    # Input: string with message to display
    # Output: image displayed on LCD
    # Notes:


outside_aqi = aqi_api('@3894')
sensor_aqi = 1
oak_town = "Oakland AQI:" + outside_aqi[1]
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23])
lcd.write_string(oak_town)
lcd.cursor_pos = (1, 0)
lcd.write_string(aqiSensor())

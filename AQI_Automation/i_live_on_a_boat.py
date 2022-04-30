# pylint: disable=unused-import
import requests
from api_key import api_key
import time
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.uart import PM25_UART
import serial
from RPLCD import CharLCD

#include neopixel lib later


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
    return [aqi, pm25['v']]

def aqiSensor():
    connection_Flag = True
    while connection_Flag:
        reset_pin.value = False
        reset_pin.value = True

        try:
            # attempt to recieve data from sensor
            aqdata = pm25.read()
            # if aqdata is properly read, break from whileloop
            connection_Flag = False
        # If unable to connect, continue looping
        except RuntimeError:
            continue

        return [aqdata["pm10 standard"], aqdata["pm25 standard"]]


def LCD_Setup():
    # Input: string with message to display
    # Output: image displayed on LCD
    # Notes:


# -------- Main --------
# Initialize Reset Pin
reset_pin = DigitalInOut(board.D0)
reset_pin.direction = Direction.OUTPUT
reset_pin.value = False

# Initialize UART pin
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
pm25 = PM25_UART(uart, reset_pin)

# LCD Setup
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23])

# Collect current AQI Measurements
outside_aqi = aqi_api('@3894')
sensor_aqi = aqiSensor()
oak_town = "Oakland AQI: " + outside_aqi[0] + "   pm2.5: " + outside_aqi[1]
boat_town = "Boat pm2.5: " + sensor_aqi[1] + "\tpm1: " + sensor_aqi[0]
lcd.write_string(oak_town)
lcd.cursor_pos = (1, 0)
lcd.write_string(aqiSensor())

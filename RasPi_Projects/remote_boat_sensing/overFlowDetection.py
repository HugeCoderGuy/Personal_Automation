#!/user/bin/python

# https://circuitdigest.com/microcontroller-projects/basic-gpio-control-on-raspberry-pi-zero-w-blinking-an-led
# sudo apt-get install rpi.gpio

import RPi.GPIO as gpio
import SMS
import time
from gmail_info import contacts


#TODO make sure pi is using least current necessary
# pin defs
sump_pin = 27
bilge_pin = 22
continue_from_boot_pin = 26  # botton left 2 pin if board is oriented so pins in top right

# board setup
gpio.setmode(gpio.BCM) # gpio numbers instead of board pin numbers
gpio.setup(sump_pin, gpio.IN)
gpio.setup(bilge_pin, gpio.IN)
gpio.setup(continue_from_boot_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

past_sump_state = gpio.input(sump_pin)
past_bilge_state = gpio.input(bilge_pin)
bilge_change = False
sump_change = False

sign_off = "\n-Pi Zero"

try:
    SMS.send_message(contacts["Alex"][0], contacts["Alex"][0], 
                        f"Beginning remote monitoring of the boat{sign_off}")
    while gpio.input(continue_from_boot_pin):
        sump_state = gpio.input(sump_pin)
        bilge_state = gpio.input(bilge_pin)
        
        if past_bilge_state != bilge_state:
            bilge_change = True
        if past_sump_state != sump_state:
            sump_change = True
        
        
        if sump_state == True and sump_change == True:
            SMS.send_msg_to_all(f"[Warning] The holding tank has reached sensor hieght{sign_off}")
        elif sump_state == False and sump_change == True:
            SMS.send_msg_to_all(f"[Info] The holding tank has been emptied!{sign_off}")
            
        if bilge_state == True and bilge_change == True:
            SMS.send_msg_to_all("[WARNING!] The bilge appears to be at an unexpected hieght." + 
                                f"This could be due to a bad sesnor reading.{sign_off}")
        elif bilge_state == False and bilge_change == True:
            SMS.send_msg_to_all(f"[Info] The bilge has returned to an expected water hieght{sign_off}")
            
        past_bilge_state = bilge_state
        past_sump_state = sump_state
        bilge_change, sump_change = False, False
        time.sleep(60*15) # sleep 15 mins
    
finally:
    SMS.send_message(contacts["Alex"][0], contacts["Alex"][0], 
                    f"Ending session.{sign_off}")

    
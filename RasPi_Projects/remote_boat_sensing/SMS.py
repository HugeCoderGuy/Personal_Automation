#!/user/bin/python

# https://testingonprod.com/2021/10/24/how-to-send-text-messages-with-python-for-free/
import smtplib

from gmail_info import EMAIL, PASSWORD, contacts
import smtplib
import sys


CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
}


def send_message(phone_number, carrier, message):
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    server.sendmail(auth[0], recipient, message)
    
def send_msg_to_all(msg):
    for person, (number, carrier) in contacts.items():
        send_message(number, carrier, msg)


if __name__ == "__main__":

    for person, (number, carrier) in contacts.items():
        message = f"Hello {person}! This is Alex's python script attempting to say hello."

        print(person, number, carrier)

    print("Text have been sent!")
#!/usr/bin/env python

from GmailWrapper import GmailWrapper

import RPi.GPIO as GPIO
import time

HOSTNAME = 'imap.gmail.com'
USERNAME = 'cat-feeder@daveshep.net.nz'
PASSWORD = 'vhov zueo fyas bkxd'

GPIO_PIN = 11

def feedByGmail():
    gmailWrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    ids = gmailWrapper.getIdsBySubject('feed cats')
    if(len(ids) > 0):
        try:
            feed()
            gmailWrapper.markAsRead(ids)
        except:
            print("Failed to feed cats, they're starvingggg")

def feed():
    # let the GPIO library know where we've connected our servo to the Pi
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.OUT)

    try:
        servo = GPIO.PWM(GPIO_PIN, 50)
        servo.start(0)

        # spin left, right, then left again rather than in a continuous circle
        # to prevent the food from jamming the servo
        for index in range(0, 3):
            dutyCycle = 4.2 if (index % 2 == 0) else 11.25
            servo.ChangeDutyCycle(dutyCycle)
            # adjust the sleep time to have the servo spin longer or shorter in that direction
            time.sleep(0.8)
    finally:
        # always cleanup after ourselves
        servo.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    # feed by receiving email
    feedByGmail()

    # kick off the feeding process (move the servo)
    #feed()


# This file is the top level programme control for the cat-feeder

### Initialise

# Servo parameters
Period = 1/50


# Wait for email instructions

# Parse email instructions

# Do instructions

# Handle any errors

# Email response

# Tidy up

### Utility functions ###

# Calculate servo duty cycle from desired angle
def calculateDutyCycle( angle ) :
    return





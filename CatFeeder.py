#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

def feed():
    # let the GPIO library know where we've connected our servo to the Pi
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)

    try:
        servo = GPIO.PWM(11, 50)
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
    # kick off the feeding process (move the servo)
    feed()
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





#!/usr/bin/env python

from GmailWrapper import GmailWrapper

import RPi.GPIO as GPIO
import time
import logging

HOSTNAME = 'imap.gmail.com'
USERNAME = 'cat-feeder@daveshep.net.nz'
PASSWORD = 'vhov zueo fyas bkxd'
SUBJECT_FEED = 'feed cats'  # case insensitive

GPIO_PIN = 11


# dutycycle calculation for Jaycar YM2763 servo
def dutycycle(angle):
    return ((angle + 90) / 20.0 + 3.0)  # -90.0 < angle < +90.0


def feedByGmail():
    logging.info("checking email at " + USERNAME)
    gmailWrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    ids = gmailWrapper.getIdsBySubject(SUBJECT_FEED)
    if (len(ids) > 0):
        logging.info("got %d email to " + SUBJECT_FEED, len(ids))
        try:
            feed()
            gmailWrapper.markAsRead(ids)
            logging.info("cats fed successfully")
            # print("Cats feed successfully")
        except Exception as e:
            logging.error("FAILED to feed cats.  %s", e)
            # print("FAILED to feed cats", e)
    else:
        logging.info("nothing to do")
        # print("Nothing to do")


def feed():
    # let the GPIO library know where we've connected our servo to the Pi
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.OUT)

    try:
        servo = GPIO.PWM(GPIO_PIN, 50)
        servo.start(0)

        # start in neutral position
        servo.ChangeDutyCycle(dutycycle(0.0))
        time.sleep(0.5)

        # spin to -60 deg
        servo.ChangeDutyCycle(dutycycle(-60.0))
        time.sleep(0.5)

        # spin to +60 deg
        servo.ChangeDutyCycle(dutycycle(+60.0))
        time.sleep(0.5)

        # end in neutral position
        servo.ChangeDutyCycle(dutycycle(0.0))
        time.sleep(0.5)


    finally:
        # always cleanup after ourselves
        servo.stop()
        GPIO.cleanup()


if __name__ == '__main__':
    # configure logging
    logging.basicConfig(filename="feeder.log",
                        level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

    # feed by receiving email
    feedByGmail()

    # kick off the feeding process (move the servo)
#    feed()


# This file is the top level programme control for the cat-feeder

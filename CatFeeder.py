#!/usr/bin/env python

from GmailWrapper import GmailWrapper
from datetime import datetime

import RPi.GPIO as GPIO
import time
import logging
import os

HOSTNAME = 'imap.gmail.com'
USERNAME = 'cat-feeder@daveshep.net.nz'
PASSWORD = 'vhov zueo fyas bkxd'
SUBJECT_FEED = 'FEED CATS'  # case insensitive
SUBJECT_PHOTO = 'TAKE PHOTO'

GPIO_PIN = 11

WORKING_DIRECTORY = '/home/pi/dev/cat-feeder/'


# check emails for a photo request, take webcam photo and send as reply
def sendPhoto():
    logging.info("checking email at " + USERNAME)
    gmailWrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    photoEmails = gmailWrapper.getIdsBySubject(SUBJECT_PHOTO)
    if (len(photoEmails) > 0):
        logging.info("got %d email to " + SUBJECT_PHOTO, len(photoEmails))
        try:
            # make filename with timestamp
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("%Y%m%d-%H%M")
            photoFilename = WORKING_DIRECTORY + timestampStr + '.jpg'

            # take photo
            os.system('fswebcam --jpeg 95 --save ' + photoFilename)

            # send as email attachment

            logging.info('saved' + photoFilename)

        except Exception as e:
            logging.error("FAILED to" + SUBJECT_PHOTO, "%s", e)

    else:
        logging.info("no photos to take")


# dutycycle calculation for Jaycar YM2763 servo
def dutycycle(angle):
    return ((angle + 90) / 20.0 + 3.0)  # -90.0 < angle < +90.0


def feedByGmail():
    logging.info("checking email at " + USERNAME)
    gmailWrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    feedEmails = gmailWrapper.getIdsBySubject(SUBJECT_FEED)
    if (len(feedEmails) > 0):
        logging.info("got %d email to " + SUBJECT_FEED, len(feedEmails))
        try:
            feed()
            gmailWrapper.markAsRead(feedEmails)
            logging.info("completed successfully")
        except Exception as e:
            logging.error("FAILED to" + SUBJECT_FEED, "%s", e)
    else:
        logging.info("no feeding to do")


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
    logging.basicConfig(filename=WORKING_DIRECTORY + "feeder.log",
                        level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

    # feed by receiving email
    feedByGmail()

    # kick off the feeding process (move the servo)
#    feed()


# This file is the top level programme control for the cat-feeder

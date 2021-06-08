#!/usr/bin/env python

import logging
import os
import time
from datetime import datetime

import RPi.GPIO as GPIO

from GmailWrapper import GmailWrapper

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
    gmail_wrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    photo_emails = gmail_wrapper.getIdsBySubject(SUBJECT_PHOTO)
    if len(photo_emails) == 0:
        logging.info('no photos to take')

    else:
        logging.info("got %d email to " + SUBJECT_PHOTO, len(photo_emails))
        try:
            # make filename with timestamp
            date_time_obj = datetime.now()
            timestamp = date_time_obj.strftime("%Y%m%d-%H%M")
            photo_filename = WORKING_DIRECTORY + timestamp + '.jpg'

            # take photo
            os.system('fswebcam --jpeg 95 --save ' + photo_filename)
            logging.info('saved ' + photo_filename)

            # get reply address
            reply_address = gmail_wrapper.getReplyTo(photo_emails[0])
            logging.info('reply address is ' + reply_address)

            # send as email attachment
            gmail_wrapper.sendImagefile('cat feeder photo at ' + timestamp, reply_address, photo_filename)
            logging.info('email sent')

        except Exception as e:
            logging.error('FAILED to ' + SUBJECT_PHOTO, '%s', e)


# dutycycle calculation for Jaycar YM2763 servo
def dutycycle(angle):
    return (angle + 90) / 20.0 + 3.0  # -90.0 < angle < +90.0


def feedByGmail():
    logging.info('checking email at ' + USERNAME)
    gmail_wrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
    feed_emails = gmail_wrapper.getIdsBySubject(SUBJECT_FEED)
    if len(feed_emails) == 0:
        logging.info('no feeding to do')
    else:
        logging.info('got %d email to ' + SUBJECT_FEED, len(feed_emails))
        try:
            feed()
            gmail_wrapper.markAsRead(feed_emails)
            logging.info('completed successfully')
        except Exception as e:
            logging.error('FAILED to' + SUBJECT_FEED, '%s', e)


def feed():
    # let the GPIO library know where we've connected our servo to the Pi
    global servo
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
    logging.basicConfig(filename=WORKING_DIRECTORY + 'feeder.log',
                        level=logging.INFO,
                        format='%(asctime)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

    # feed by receiving email
    feedByGmail()

    # send photo to requesting email
    sendPhoto()

    # kick off the feeding process (move the servo)
#    feed()

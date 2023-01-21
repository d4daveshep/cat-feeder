#!/usr/bin/env python

import logging
import os
import subprocess
import time
from datetime import datetime

import RPi.GPIO as GPIO

from gmail_wrapper import GmailWrapper

WORKING_DIRECTORY = os.path.dirname(__file__) + '/'  # was '/home/pi/dev/cat-feeder/'
LOG_FILE = WORKING_DIRECTORY + 'logs/feeder.log'


# take a webcam photo, storing it in working directory and returning the file path & name
def take_photo(working_directory='/tmp/'):
    date_time_obj = datetime.now()
    timestamp = date_time_obj.strftime("%Y%m%d-%H%M")
    filename = WORKING_DIRECTORY + timestamp + '.jpg'

    # take photo (skip a large number of frames to allow camera to adjust to lighting etc)
    cp = subprocess.run(['fswebcam -S 200 --jpeg 95 --save ' + filename],
                        shell=True, capture_output=True, universal_newlines=True)

    # cp.returncode is not working properly so check specifically if filename was created
    if os.path.exists(filename) is False:
        msg = 'Failed to capture photo. Check webcam is connected and working'
        raise Exception(msg)
    else:
        logging.debug(cp.stdout)
        logging.info('saved ' + filename)
        return filename


# dutycycle calculation for Jaycar YM2763 servo
def dutycycle(angle):
    return (angle + 90) / 20.0 + 3.0  # -90.0 < angle < +90.0


def feed():
    GPIO_PIN = 11

    # let the GPIO library know where we've connected our servo to the Pi
    global servo
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.OUT)

    cycles = 3  # how many cycles do we want to run - this affects how much is dispensed
    angle = 89.0  # rotation angle positive and negative

    try:
        servo = GPIO.PWM(GPIO_PIN, 50)
        servo.start(0)

        # start in neutral position
        servo.ChangeDutyCycle(dutycycle(0.0))
        time.sleep(0.5)

        count = 0  # current cycle count
        while count < cycles:
            # spin to -ve deg
            servo.ChangeDutyCycle(dutycycle(-angle))
            time.sleep(1.0)

            # spin to +ve deg
            servo.ChangeDutyCycle(dutycycle(+angle))
            time.sleep(1.0)

            count = count + 1

        # always end in neutral position
        servo.ChangeDutyCycle(dutycycle(0.0))
        time.sleep(0.5)

    finally:
        # always cleanup after ourselves
        servo.stop()
        GPIO.cleanup()


def email_actions():
    email_username = "dev.catfeeder123@gmail.com"
    logging.info('checking email at ' + email_username)
    gmail_wrapper = GmailWrapper("imap.gmail.com", email_username, "qqdv jxwo cotb msbd")

    nothing_to_do = True

    # check for feed emails
    feed_subject = "FEED CATS"
    feed_emails = gmail_wrapper.get_IDs_by_subject(feed_subject)
    if len(feed_emails) > 0:
        logging.info('got %d email to ' + feed_subject, len(feed_emails))
        nothing_to_do = False
        try:
            feed()
            gmail_wrapper.mark_as_read(feed_emails)
            logging.info('fed cats successfully')
        except Exception as e:
            logging.error('FAILED to' + feed_subject, '%s', e)

    # check for take photo emails
    photo_subject = "TAKE PHOTO"
    photo_emails = gmail_wrapper.get_IDs_by_subject(photo_subject)
    if len(photo_emails) > 0:
        logging.info("got %d email to " + photo_subject, len(photo_emails))
        nothing_to_do = False

        try:
            # take photo
            photo_filename = take_photo(WORKING_DIRECTORY)

            # get reply address
            reply_address = gmail_wrapper.get_reply_to(photo_emails[0])
            logging.info('reply address is ' + reply_address)

            # send as email attachment
            gmail_wrapper.send_image_file('cat feeder photo', reply_address, photo_filename)
            logging.info('photo taken and sent')

            gmail_wrapper.mark_as_read(photo_emails)

            # TODO add this as an option too
            # delete the image file
            os.system('rm ' + photo_filename)
            logging.info('deleted ' + photo_filename)

        except Exception as e:
            logging.error('FAILED to ' + photo_subject + ': ' + str(e))

    get_log_subject = "GET LOG"
    get_log_emails = gmail_wrapper.get_IDs_by_subject(get_log_subject)
    if len(get_log_emails) > 0:
        logging.info("got %d email to " + get_log_subject, len(get_log_emails))
        nothing_to_do = False

        try:
            reply_address = gmail_wrapper.get_reply_to(get_log_emails[0])
            logging.info('reply address is ' + reply_address)

            # send as email attachment
            gmail_wrapper.send_text_file('cat feeder log file', reply_address, LOG_FILE)
            logging.info('log file sent')

            gmail_wrapper.mark_as_read(get_log_emails)

        except Exception as e:
            logging.error('FAILED to ' + get_log_subject + ': ' + str(e))

    if nothing_to_do is True:
        logging.info('nothing to do')

    gmail_wrapper.logout()
    logging.info('logged out from email server')


if __name__ == '__main__':
    # configure logging
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    # email actions
    email_actions()

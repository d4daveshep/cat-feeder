#!/usr/bin/env python

import logging
import os
import subprocess
import time
from datetime import datetime

import RPi.GPIO as GPIO

from GmailWrapper import GmailWrapper

HOSTNAME = 'imap.gmail.com'
USERNAME = 'cat-feeder@daveshep.net.nz'
PASSWORD = 'vhov zueo fyas bkxd'
SUBJECT_FEED = 'FEED CATS'  # case insensitive
SUBJECT_PHOTO = 'TAKE PHOTO'
SUBJECT_GET_LOG = 'GET LOG'

GPIO_PIN = 11

WORKING_DIRECTORY = os.path.dirname(__file__) + '/'  # was '/home/pi/dev/cat-feeder/'
LOG_FILE = WORKING_DIRECTORY + 'logs/feeder.log'


# check emails for a photo request, take webcam photo and send as reply
# def sendPhoto():
#     logging.info("checking email at " + USERNAME)
#     gmail_wrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
#     photo_emails = gmail_wrapper.getIdsBySubject(SUBJECT_PHOTO)
#
#     if len(photo_emails) == 0:
#         logging.info('no photos to take')
#
#     else:
#         logging.info("got %d email to " + SUBJECT_PHOTO, len(photo_emails))
#         try:
#             # take photo
#             photo_filename = takePhoto(WORKING_DIRECTORY)
#
#             # get reply address
#             reply_address = gmail_wrapper.getReplyTo(photo_emails[0])
#             logging.info('reply address is ' + reply_address)
#
#             # send as email attachment
#             gmail_wrapper.sendImagefile('cat feeder photo', reply_address, photo_filename)
#             logging.info('email sent')
#
#             gmail_wrapper.markAsRead(photo_emails)
#
#             ### TODO add this as an option too
#             # delete the image file
#             os.system('rm ' + photo_filename)
#             logging.info('deleted ' + photo_filename)
#
#         except Exception as e:
#             logging.error('FAILED to ' + SUBJECT_PHOTO + ': ' + str(e))


# take a webcam photo, storing it in working directory and returning the file path & name
def takePhoto(working_directory='/tmp/'):
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


# def feedByGmail():
#     logging.info('checking email at ' + USERNAME)
#     gmail_wrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
#     feed_emails = gmail_wrapper.getIdsBySubject(SUBJECT_FEED)
#     if len(feed_emails) == 0:
#         logging.info('no feeding to do')
#     else:
#         logging.info('got %d email to ' + SUBJECT_FEED, len(feed_emails))
#         try:
#             feed()
#             gmail_wrapper.markAsRead(feed_emails)
#             logging.info('completed successfully')
#         except Exception as e:
#             logging.error('FAILED to' + SUBJECT_FEED, '%s', e)


def feed():
    # let the GPIO library know where we've connected our servo to the Pi
    global servo
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.OUT)

    cycles = 2  # how many cycles do we want to run - this affects how much is dispensed
    angle = 60.0  # rotation angle positive and negative

    try:
        servo = GPIO.PWM(GPIO_PIN, 50)
        servo.start(0)

        # start in neutral position
        # servo.ChangeDutyCycle(dutycycle(0.0))
        # time.sleep(0.5)

        count = 0  # current cycle count
        while count < cycles:
            # spin to -ve deg
            servo.ChangeDutyCycle(dutycycle(-angle))
            time.sleep(1.0)

            # spin to +ve deg
            servo.ChangeDutyCycle(dutycycle(+angle))
            time.sleep(1.0)

            count = count + 1

        # always end in positive angle
        servo.ChangeDutyCycle(dutycycle(+angle))
        time.sleep(1.0)

    finally:
        # always cleanup after ourselves
        servo.stop()
        GPIO.cleanup()


def emailActions():
    logging.info('checking email at ' + USERNAME)
    gmail_wrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)

    nothing_to_do = True

    # check for feed emails
    feed_emails = gmail_wrapper.getIdsBySubject(SUBJECT_FEED)
    if len(feed_emails) > 0:
        logging.info('got %d email to ' + SUBJECT_FEED, len(feed_emails))
        nothing_to_do = False
        try:
            feed()
            gmail_wrapper.markAsRead(feed_emails)
            logging.info('fed cats successfully')
        except Exception as e:
            logging.error('FAILED to' + SUBJECT_FEED, '%s', e)

    # check for take photo emails
    photo_emails = gmail_wrapper.getIdsBySubject(SUBJECT_PHOTO)
    if len(photo_emails) > 0:
        logging.info("got %d email to " + SUBJECT_PHOTO, len(photo_emails))
        nothing_to_do = False

        try:
            # take photo
            photo_filename = takePhoto(WORKING_DIRECTORY)

            # get reply address
            reply_address = gmail_wrapper.getReplyTo(photo_emails[0])
            logging.info('reply address is ' + reply_address)

            # send as email attachment
            gmail_wrapper.sendImagefile('cat feeder photo', reply_address, photo_filename)
            logging.info('photo taken and sent')

            gmail_wrapper.markAsRead(photo_emails)

            ### TODO add this as an option too
            # delete the image file
            os.system('rm ' + photo_filename)
            logging.info('deleted ' + photo_filename)

        except Exception as e:
            logging.error('FAILED to ' + SUBJECT_PHOTO + ': ' + str(e))

    get_log_emails = gmail_wrapper.getIdsBySubject(SUBJECT_GET_LOG)
    if len(get_log_emails) > 0:
        logging.info("got %d email to " + SUBJECT_GET_LOG, len(get_log_emails))
        nothing_to_do = False

        try:
            reply_address = gmail_wrapper.getReplyTo(get_log_emails[0])
            logging.info('reply address is ' + reply_address)

            # send as email attachment
            gmail_wrapper.sendTextfile('cat feeder log file', reply_address, LOG_FILE)
            logging.info('log file sent')

            gmail_wrapper.markAsRead(get_log_emails)


        except Exception as e:
            logging.error('FAILED to ' + SUBJECT_GET_LOG + ': ' + str(e))

    if nothing_to_do is True:
        logging.info('nothing to do')


if __name__ == '__main__':
    # configure logging
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    # email actions
    emailActions()

    # feed by receiving email
    # feedByGmail()

    # send photo to requesting email
    # sendPhoto()

    # kick off the feeding process (move the servo)
#    feed()

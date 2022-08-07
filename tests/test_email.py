import smtplib
import ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest

from gmail_wrapper import GmailWrapper


@pytest.fixture()
def email_app_pwd():
    return "qukd oiup sfjb vmyc"


@pytest.fixture()
def email_address():
    return "dev.catfeeder.123@gmail.com"


@pytest.fixture()
def gmail_wrapper(email_app_pwd, email_address):
    email_host = "imap.gmail.com"

    return GmailWrapper(email_host, email_address, email_app_pwd)


def test_check_for_new_email(gmail_wrapper, email_app_pwd, email_address):
    feed_subject = "FEED CATS"

    assert gmail_wrapper is not None  # check imap object is valid

    feed_emails = gmail_wrapper.getIdsBySubject(feed_subject)  # get mail IDs matching feed subject
    gmail_wrapper.markAsRead(feed_emails)  # mark them as reed

    gmail_wrapper.send_plain_email(feed_subject, email_address, f"test message: {feed_emails}")

    feed_emails = gmail_wrapper.getIdsBySubject(feed_subject)  # get the mail IDs again
    assert len(feed_emails) == 1  # we should have one new one

    gmail_wrapper.markAsRead(feed_emails)  # mark it as read

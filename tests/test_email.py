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
def gmail_imap_wrapper(email_app_pwd, email_address):
    email_host = "imap.gmail.com"

    return GmailWrapper(email_host, email_address, email_app_pwd)


@pytest.fixture()
def gmail_smtp_wrapper(email_app_pwd, email_address):
    smtp_server = "smtp.gmail.com"
    port = 587  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(email_address, email_app_pwd)

        yield server

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()


def test_send_plain_email(email_address, email_app_pwd):

    feed_subject = "FEED CATS"

    # create email object that has multiple part
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = Header(feed_subject, 'utf-8').encode()

    # add message content
    msg_content = MIMEText(f"test message command: {feed_subject}", 'plain', 'utf-8')
    msg.attach(msg_content)

    # Create a secure SSL context
    smtp_server = "smtp.gmail.com"
    port = 587  # For SSL
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(email_address, email_app_pwd)
        server.sendmail(email_address, email_address, msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()


def test_check_for_new_email(gmail_imap_wrapper, gmail_smtp_wrapper, email_app_pwd, email_address):
    feed_subject = "FEED CATS"

    assert gmail_imap_wrapper is not None  # check imap object is valid

    feed_emails = gmail_imap_wrapper.getIdsBySubject(feed_subject)  # get mail IDs matching feed subject
    gmail_imap_wrapper.markAsRead(feed_emails)  # mark them as reed

    # build a test message to send to our email address
    body = f"test message to {feed_subject}"
    message = f"From: {email_address}\nTo: {email_address}\nSubject: {feed_subject}\n\n{body}"
    gmail_smtp_wrapper.sendmail(email_address, email_address, message)  # send the message

    feed_emails = gmail_imap_wrapper.getIdsBySubject(feed_subject)  # get the mail IDs again
    assert len(feed_emails) == 1  # we should have one new one

    gmail_imap_wrapper.markAsRead(feed_emails)  # mark it as read

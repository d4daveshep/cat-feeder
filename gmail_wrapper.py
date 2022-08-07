#!/usr/bin/env python

import email
import logging
import os.path
import smtplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from imapclient import IMAPClient, SEEN

SEEN_FLAG = 'SEEN'
UNSEEN_FLAG = 'UNSEEN'


class GmailWrapper:
    def __init__(self, host, username, password):
        #   force the user to pass along username and password to log in as
        self.host = host
        self.userName = username
        self.password = password
        self.login()

    def login(self):
        logging.debug('Logging in as ' + self.userName)
        server = IMAPClient(self.host, use_uid=True, ssl=True)
        server.login(self.userName, self.password)
        self.server = server

    def logout(self):
        logging.debug('Logging out of IMAPClient from GmailWrapper')
        self.server.logout()

    #   The IMAPClient search returns a list of Id's that match the given criteria.
    #   An Id in this case identifies a specific email
    def getIdsBySubject(self, subject, unreadonly=True, folder='INBOX'):
        #   search within the specified folder, e.g. Inbox
        self.setFolder(folder)

        #   build the search criteria (e.g. unread emails with the given subject)
        self.searchCriteria = [UNSEEN_FLAG, 'SUBJECT', subject]

        if unreadonly is False:
            #   force the search to include "read" emails too
            self.searchCriteria.append(SEEN_FLAG)

        #   conduct the search and return the resulting Ids
        return self.server.search(self.searchCriteria)

    def markAsRead(self, mail_ids, folder='INBOX'):
        self.setFolder(folder)
        self.server.set_flags(mail_ids, [SEEN])

    def setFolder(self, folder):
        self.server.select_folder(folder)

    def getReplyTo(self, message_id, folder='INBOX'):
        self.setFolder(folder)
        message_data = self.server.fetch([message_id], 'RFC822').get(message_id)
        email_message = email.message_from_bytes(message_data[b'RFC822'])
        email_return_path = email_message.get('Return-Path')
        address = email_return_path[1:len(email_return_path) - 1]
        return address

        # message = email.message_from_bytes(message_data)
        # return message_data

    def sendImagefile(self, subject, to_address, filename):
        # create email object that has multiple part
        msg = MIMEMultipart()
        msg['From'] = self.userName
        msg['To'] = to_address
        msg['Subject'] = Header(subject, 'utf-8').encode()

        # add message content
        msg_content = MIMEText('photo attached is ' + os.path.basename(filename), 'plain', 'utf-8')
        msg.attach(msg_content)

        # read the image file
        fp = open(filename, 'rb')
        img = MIMEImage(fp.read())
        fp.close()

        # add the image
        img.add_header('Content-Disposition', 'attachment; filename=' + os.path.basename(filename))
        msg.attach(img)

        # send message securely
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(self.userName, self.password)
        smtp.sendmail(self.userName, to_address, msg.as_string())
        smtp.quit()

    def sendTextfile(self, subject, to_address, filename):
        # create email object that has multiple part
        msg = MIMEMultipart()
        msg['From'] = self.userName
        msg['To'] = to_address
        msg['Subject'] = Header(subject, 'utf-8').encode()

        # add message content
        msg_content = MIMEText('log file attached is ' + os.path.basename(filename), 'plain', 'utf-8')
        msg.attach(msg_content)

        # read the text file
        fp = open(filename, 'r')
        text = MIMEText(fp.read())
        fp.close()

        # add the image
        text.add_header('Content-Disposition', 'attachment; filename=' + os.path.basename(filename))
        msg.attach(text)

        # send message securely
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(self.userName, self.password)
        smtp.sendmail(self.userName, to_address, msg.as_string())
        smtp.quit()

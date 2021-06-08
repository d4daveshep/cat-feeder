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

    #   The IMAPClient search returns a list of Id's that match the given criteria.
    #   An Id in this case identifies a specific email
    def getIdsBySubject(self, subject, unreadOnly=True, folder='INBOX'):
        #   search within the specified folder, e.g. Inbox
        self.setFolder(folder)

        #   build the search criteria (e.g. unread emails with the given subject)
        self.searchCriteria = [UNSEEN_FLAG, 'SUBJECT', subject]

        if unreadOnly == False:
            #   force the search to include "read" emails too
            self.searchCriteria.append(SEEN_FLAG)

        #   conduct the search and return the resulting Ids
        return self.server.search(self.searchCriteria)

    def markAsRead(self, mailIds, folder='INBOX'):
        self.setFolder(folder)
        self.server.set_flags(mailIds, [SEEN])

    def setFolder(self, folder):
        self.server.select_folder(folder)

    def getReplyTo(self, messageID, folder='INBOX'):
        self.setFolder(folder)
        message_data = self.server.fetch([messageID], 'RFC822').get(messageID)
        email_message = email.message_from_bytes(message_data[b'RFC822'])
        email_return_path = email_message.get('Return-Path')
        address = email_return_path[1:len(email_return_path) - 1]
        return address

        # message = email.message_from_bytes(message_data)
        # return message_data

    def sendImagefile(self, subject, address, filename):
        # create email object that has multiple part:
        msg = MIMEMultipart()
        msg['From'] = self.userName
        msg['To'] = address
        msg['Subject'] = Header(subject, 'utf-8').encode()

        msg_content = MIMEText('photo attached is ' + os.path.basename(filename), 'plain', 'utf-8')
        msg.attach(msg_content)

        fp = open(filename, 'rb')
        img = MIMEImage(fp.read())
        fp.close()

        img.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))
        img.add_header()
        msg.attach(img)

        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(self.userName, self.password)
        smtp.sendmail(self.userName, address, msg.as_string())
        smtp.quit()





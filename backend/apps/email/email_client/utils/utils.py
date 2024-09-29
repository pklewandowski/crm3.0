import email
import imaplib

import crm_settings


class EmailClient:
    def __init__(self, user, password, hostname=crm_settings.EMAIL_COMPANY_HOST):
        self.hostname = hostname
        self.user = user
        self.password = password
        self.connection = self.get_connection_ssl()

    def get_connection_ssl(self):
        conn = imaplib.IMAP4_SSL(self.hostname)
        conn.login(self.user, self.password)
        conn.select()
        return conn

    def get_messages(self, conditions=None):
        typ, data = self.connection.search(None, 'ALL')
        for num in data[0].split():
            typ, data = self.connection.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            # for payload in msg.get_payload():
            print(msg.get_payload())
            # print('Message %s\n%s\n' % (num, data[0][1]))

    def logout(self):
        if self.connection:
            self.connection.close()
            self.connection.logout()

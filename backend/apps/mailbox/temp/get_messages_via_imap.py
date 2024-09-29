import email
import imaplib

m = imaplib.IMAP4_SSL("serwer2371323.home.pl")
m.login("info@3ws.pl", "password")
m.select('inbox')

status, data = m.search(None, 'ALL')

for num in data[0].split():
    status, data = m.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1], policy=email.policy.default)

    # body = ""
    # for part in msg.walk():
    #     charset = part.get_content_charset()
    #     if part.get_content_type() == "text/plain":
    #         partStr = part.get_payload(decode=True)
    #         body += partStr.decode(charset)
    #
    # print(body)

    body = msg.get_payload(decode=True)
    if body is not None:
        body = body.decode(msg.get_content_charset())

    print('From:', msg['From'])
    print('Subject:', msg['Subject'])
    print('Date:', msg['Date'])
    print('Body:', body) # msg.get_payload(decode=True).decode(msg.get_content_charset()))
    print()

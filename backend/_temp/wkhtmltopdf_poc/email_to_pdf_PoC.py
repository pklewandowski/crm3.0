import email
import os

import pdfkit
from pyvirtualdisplay import Display

TEST_EMAIL_FILENAME = 'test_email_4'
# path to wkhtmltopdf executable
if os.name == 'nt':
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

PATH = os.path.join(os.path.dirname(__file__), f'{TEST_EMAIL_FILENAME}.pdf')

config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
options = {
    "enable-local-file-access": None,
    'encoding': "UTF-8",
    'load-error-handling': 'ignore'
}


def get_eml_body(eml_file_name: str):
    """
    Extract body from .eml email message file
    :param eml_file_name: .eml email file name
    :return: .eml email file body in html / text format
    """
    eml_body = ''

    with open(eml_file_name, encoding='utf-8') as f:
        msg = email.message_from_file(f)

        if msg.is_multipart():
            for part in msg.get_payload():
                eml_body += part.get_payload(decode=True).decode()
        else:
            eml_body = msg.get_payload(decode=True).decode()

    return eml_body


def html_to_pdf(html_str: str):
    """
    Generic method for converting html content to pdf document
    :param html_str: html string content of the source document
    """
    if os.name == 'nt':
        pdfkit.from_string(input=html_str, output_path=PATH, configuration=config, options=options)
    else:
        # needed for linux error wkhtmltopdf cannot connect to x-display
        with Display():
            pdfkit.from_string(input=html_str, output_path=PATH, configuration=config, options=options)


if __name__ == '__main__':
    html_to_pdf(get_eml_body(f'{TEST_EMAIL_FILENAME}.eml'))

from django.core.mail import EmailMessage


def send_message(to, subject, body, cc=None):
    return
    email = EmailMessage(subject=subject, body=body, to=to, cc=cc)
    email.send(fail_silently=False)


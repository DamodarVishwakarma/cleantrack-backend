from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage

def send_email(send_email, subject, *args, **email_data):
    email_from = settings.EMAIL_HOST_USER
    message = get_template('email.html').render(email_data)
    msg = EmailMessage(
        subject,
        message,
        email_from,
        send_email,
    )

    msg.content_subtype = "html"
    msg.send()


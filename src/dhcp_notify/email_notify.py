import smtplib
from email.message import EmailMessage

from . import config


def make_email(msg_config, msg_text):
    msg = EmailMessage()
    msg["From"] = msg_config.from_addr
    msg["To"] = msg_config.to_addr
    msg["Subject"] = msg_config.subject
    msg.set_content(msg_text)
    return msg


def send_email(smtp_config, message):
    if smtp_config.tls is config.SMTPTLSConfig.tls:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    with smtp_class(host=smtp_config.host, port=smtp_config.port) as smtp:
        if smtp_config.tls is config.SMTPTLSConfig.starttls:
            smtp.starttls()

        if smtp_config.credentials:
            smtp.login(
                user=smtp_config.credentials.username,
                password=smtp_config.credentials.password,
            )

        smtp.send_message(message)

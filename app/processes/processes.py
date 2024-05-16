import smtplib

from app.core.config import settings
from app.processes.celery import celery
from app.processes.email_templates import get_email_template


@celery.task()
def send_verify_email(user_id: int, email: str):
    with smtplib.SMTP_SSL(settings.mail_settings.host, settings.mail_settings.port) as server:
        server.login(settings.mail_settings.username, settings.mail_settings.password)
        email = get_email_template(user_id=user_id, email_addr=email)
        server.send_message(email)

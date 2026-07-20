import smtplib

from app.core.config import settings
from app.processes.celery import celery
from app.processes.email_templates import (
    get_email_template_verify,
    get_email_template_new_ip,
)


@celery.task()
def send_verify_email(user_id: int, email: str):
    with smtplib.SMTP_SSL(
        settings.mail_settings.host, settings.mail_settings.port
    ) as server:
        server.login(settings.mail_settings.username, settings.mail_settings.password)
        message = get_email_template_verify(user_id=user_id, email_addr=email)
        server.send_message(message)


@celery.task()
def send_email_new_ip(user_id: int, email: str, request_ip: str):
    # user_id kept for Celery task signature / logging compatibility
    _ = user_id
    with smtplib.SMTP_SSL(
        settings.mail_settings.host, settings.mail_settings.port
    ) as server:
        server.login(settings.mail_settings.username, settings.mail_settings.password)
        message = get_email_template_new_ip(email_addr=email, request_ip=request_ip)
        server.send_message(message)

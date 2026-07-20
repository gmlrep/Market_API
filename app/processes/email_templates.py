from email.message import EmailMessage
from datetime import timedelta

from app.core.config import settings
from app.core.security import create_jwt


def get_email_template_verify(user_id: int, email_addr: str) -> EmailMessage:
    token = create_jwt(
        token_data={"sub": str(user_id)},
        token_type="set_password",
        expires_delta=timedelta(days=1),
    )
    email = EmailMessage()
    email["Subject"] = "Verify URL"
    email["From"] = settings.mail_settings.mail_from
    email["To"] = email_addr

    email.set_content(
        f"""
                <p>https://example.com/token/{token}</p>
            """,
        subtype="html",
    )
    return email


def get_email_template_new_ip(email_addr: str, request_ip: str) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = "New device login"
    email["From"] = settings.mail_settings.mail_from
    email["To"] = email_addr

    email.set_content(
        f"""
                    <p>Вход с нового устройства. IP - {request_ip}</p>
                """,
        subtype="html",
    )
    return email

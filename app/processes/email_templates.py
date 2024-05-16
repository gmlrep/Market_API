from datetime import timedelta
from email.message import EmailMessage

from app.core.config import settings
from app.core.security import create_jwt


def get_email_template_verify(user_id: int, email_addr: str):
    token = create_jwt(token_data={'sub': user_id}, token_type='set_password', expires_delta=timedelta(days=1))
    email = EmailMessage()
    email['Subject'] = 'Verify URL'
    email['From'] = settings.mail_settings.mail_from
    email['To'] = email_addr

    email.set_content(
        f""" 
                <p>https://example.com/token{token}</p>
            """,
        subtype='html'
    )
    return email


def get_email_template_new_ip(user_id: int, email_addr: str, requesst_ip: str):
    email = EmailMessage()
    email['Subject'] = 'Verify URL'
    email['From'] = settings.mail_settings.mail_from
    email['To'] = email_addr

    email.set_content(
        f""" 
                    <p>Вход с нового устройства. IP - {requesst_ip}</p>
                """,
        subtype='html'
    )
    return email

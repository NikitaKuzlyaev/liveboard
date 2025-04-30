# tasks.py
# app/email/tasks.py

import hashlib
import logging
import secrets
import smtplib
from uuid import uuid4

from app.db.models import SiteUser
from app.email.celery_app import celery_app
from app.email.schema import Letter, SmtpUser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

"""
msg = MIMEText("Привет! Это тестовое письмо.")
msg["Subject"] = "Тест"
msg["From"] = "you@example.com"
msg["To"] = "friend@example.com"

"""


def get_smtp_user() -> SmtpUser:
    """"""
    smtp_user = SmtpUser(
        name='',
        password='',
    )

    return smtp_user


def get_validation_string(
        user: SiteUser,
) -> str:
    """"""
    name_hash = hashlib.sha256(user.name.encode()).hexdigest()
    validation_string = str(name_hash) + str(uuid4())
    return validation_string


def random_validation_code(length: int = 6) -> str:
    """"""
    return ''.join(secrets.choice("0123456789") for _ in range(length))


@celery_app.task
def send_email(
        letter: Letter,
        smtp_user: SmtpUser = Depends(get_smtp_user),
):
    """"""
    with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
        server.login(smtp_user.name, smtp_user.password)
        server.send_message(msg)

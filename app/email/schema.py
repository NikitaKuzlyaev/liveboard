# schema.py
# app/email/schema.py

from email.mime.text import MIMEText

from pydantic import BaseModel, EmailStr, Field


class Letter(BaseModel):
    msg_subject: str = Field(min_length=1, max_length=64)
    msg_from: EmailStr
    msg_to: EmailStr
    msg_text: MIMEText


class SmtpUser(BaseModel):
    user: str
    password: str

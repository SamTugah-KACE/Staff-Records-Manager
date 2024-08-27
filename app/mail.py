import random
import string
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import Optional
from Config.config import settings
from models import User

# Define the email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

# Utility functions
def generate_username(first_name: str, surname: str) -> str:
    print("\nGenerated Username: ", f"{first_name.lower()}.{surname.lower()}{random.randint(100, 999)}")
    return f"{first_name.lower()}.{surname.lower()}{random.randint(100, 999)}"

def generate_password(length: int = 6) -> str:
    #characters = string.ascii_letters + string.digits + string.punctuation
    characters = string.ascii_letters + string.digits
    print("\n----------------in password-------\n--------------------------------------------------------\ncharacters: ", characters)
    print("\nGenerated Password: ", ''.join(random.choice(characters) for _ in range(length)))
    return ''.join(random.choice(characters) for _ in range(length))

# async def send_email(email: EmailStr, subject: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email],
#         body=body,
#         subtype="html"
#     )
#     fm = FastMail(conf)
#     await fm.send_message(message) #Await the coroutine

async def send_email(email: EmailStr, subject: str, body: str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        # Log the exception or retry
        print(f"Failed to send email to {email}: {e}")

# Define the email template
def get_email_template(username: str, password: str, href: str) -> str:
    return f"""
    <h2>GI-KACE Staff Records System</h2>
    <p>Your account has been created successfully. Below are your login credentials:</p>
    <p><strong>Username:</strong> {username}</p>
    <p><strong>Password:</strong> {password}</p>
    <p>Please change your password after logging in for the first time using the link: <a href='{href}'>Login</a></p>
    """

def account_emergency() -> str:
    return """
    <h2>GI-KACE Staff Records System</h2>
    <p>Your account has been <strong>disabled</strong> due to multiple intrusion attempts.</p>
    <p>Please contact the System's Administrator for redress.</p>

    <p>Thank you.</p>
    """
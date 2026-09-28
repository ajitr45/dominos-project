import smtplib
from email.message import EmailMessage

from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
)


def send_password_reset_email(
    recipient_email: str,
    reset_token: str,
):
    # Build the password reset link
    reset_link = (f"http://localhost:5173/reset-password?token={reset_token}")

    # Create email
    message = EmailMessage()

    message["Subject"] = "Reset your Domino's account password"
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = recipient_email

    message.set_content(
        f"""
Hello,

We received a request to reset your Domino's account password.

Use the link below to reset your password:

{reset_link}

This link will expire in 15 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
Domino's Food Ordering Team
"""
    )

    # Send email through SMTP
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)

    email_sent = True

    return email_sent
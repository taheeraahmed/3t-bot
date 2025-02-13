import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from credentials import UserCredentials


def send_email(credentials: UserCredentials, subject: str, body: str) -> None:
    """Send an email notification."""
    logger = logging.getLogger(__name__)
    try:
        msg = MIMEMultipart()
        msg["From"] = credentials.email_sender_and_reciever
        msg["To"] = credentials.email_sender_and_reciever
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(
            credentials.email_sender_and_reciever,
            credentials.email_app_pwd.get_secret_value(),
        )
        server.sendmail(
            credentials.email_sender_and_reciever,
            credentials.email_sender_and_reciever,
            msg.as_string(),
        )
        server.quit()

        logger.info("📩 Email notification sent successfully!")
    except Exception as e:
        logger.error(f"❌ Email failed to send: {e}")

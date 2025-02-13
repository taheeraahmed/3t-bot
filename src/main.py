import logging
import os
import pathlib
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, SecretStr

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
BASE_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")  # Load environment variables from .env file


class UserCredentials(BaseModel):
    gym_username: str
    gym_password: SecretStr  # Mask passwords in logs
    email_sender_and_reciever: str
    email_app_pwd: SecretStr


def get_user_credentials() -> UserCredentials:
    """Loads user credentials from environment variables and returns a validated object."""
    return UserCredentials(
        gym_username=os.getenv("GYM_USERNAME"),
        gym_password=os.getenv("GYM_PASSWORD"),
        email_sender_and_reciever=os.getenv("EMAIL_USER"),
        email_app_pwd=os.getenv("EMAIL_APP_PWD"),
    )


def send_email(credentials: UserCredentials, subject: str, body: str) -> None:
    """Send an email notification."""
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

        logging.info("📩 Email notification sent successfully!")
    except Exception as e:
        logging.error(f"❌ Email failed to send: {e}")


def book_gym_class(credentials: UserCredentials):
    with sync_playwright() as p:
        logger = logging.getLogger(__name__)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # login
        page.goto("https://www.3t.no/logg-inn")
        page.fill("input#username", credentials.gym_username)
        page.fill("input#password", credentials.gym_password.get_secret_value())
        page.locator("div.button__visible:has-text('Logg inn')").click()
        page.wait_for_load_state("networkidle")

        # navigate to booking page
        # get today's date and add 7 days
        future_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        booking_url = f"https://www.3t.no/booking/gruppetimer?FROM_DATE={future_date}&TO_DATE={future_date}"
        page.goto(booking_url)
        page.wait_for_load_state("networkidle")

        # find the list of classes
        class_list_container = page.locator(
            "div.vertical-container.vertical-container__horizontal-placement--center.vertical-container__width--full"
        )
        class_containers = class_list_container.locator("div.booking-button__main")

        # loop through all classes
        for i in range(class_containers.count()):
            container = class_containers.nth(i)

            # check if this class matches "PowerPit Total Body 60" at "11:00"
            title = container.locator("h2").inner_text()
            time = (
                container.locator("div.text__size--small.text__weight--bold")
                .nth(0)
                .inner_text()
            )

            if "PowerPit Total Body 60" in title and "11:00" in time:
                logger.info(f"Found the correct class: {title} at {time}")

                # find the button which says "Book time"
                button = container.locator("button")
                button_text = button.inner_text()

                if "Book time" in button_text:
                    button.click()
                    logger.info("✅ Class booked successfully!")

                    send_email(
                        credentials=credentials,
                        subject="✅ Gym Class Booked Successfully!",
                        body=f"You have successfully booked '{title}' on {future_date} at {time}.",
                    )
                else:
                    logger.info("❌ Class is full. Skipping waitlist.")
                    send_email(
                        credentials=credentials,
                        subject="❌ Gym Class is Full",
                        body=f"The class '{title}' on {future_date} at {time} is full. No booking was made.",
                    )

                break
        else:
            logger.info("❌ Class not found. Maybe it's not available for booking yet.")
            send_email(
                credentials=credentials,
                subject="❌ Gym Class Not Found",
                body=f"The class '{title}' on {future_date} at {time} was not found on the booking page.",
            )

        browser.close()


if __name__ == "__main__":
    credentials = get_user_credentials()

    book_gym_class(
        credentials=credentials,
    )

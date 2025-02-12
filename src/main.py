import logging
import os
import pathlib
from datetime import datetime, timedelta

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def book_gym_class(username, password, gym_url):
    with sync_playwright() as p:
        logger = logging.getLogger(__name__)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # login
        page.goto(gym_url)
        page.fill("input#username", username)
        page.fill("input#password", password)
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
                else:
                    logger.info("❌ Class is full. Skipping waitlist.")

                break
        else:
            logger.info("❌ Class not found. Maybe it's not available for booking yet.")

        browser.close()


if __name__ == "__main__":
    BASE_DIR = pathlib.Path(__file__).parent.parent
    load_dotenv(BASE_DIR / ".env")  # Load environment variables from .env file

    username = os.getenv("GYM_USERNAME")
    password = os.getenv("GYM_PASSWORD")

    book_gym_class(
        username=username,
        password=password,
        gym_url="https://www.3t.no/logg-inn",
    )

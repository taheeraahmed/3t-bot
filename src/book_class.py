import logging
import time
from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from credentials import UserCredentials
from send_mail import send_email


def wait_for_page_to_load(logger, page, browser):
    try:
        logger.info("⏳ Waiting for page to load...")
        page.wait_for_load_state("load", timeout=60000)
    except PlaywrightTimeoutError:
        logger.error("❌ Page load timeout! Printing page content for debugging.")
        with open("error_page.html", "w") as f:
            f.write(page.content())  # Save page content for debugging
        browser.close()
        raise  # Re-raise the error to stop execution

    logger.info("✅ Page loaded successfully!")


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

        wait_for_page_to_load(logger, page, browser)

        # navigate to booking page
        # get today's date and add 7 days
        future_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        booking_url = f"https://www.3t.no/booking/gruppetimer?FROM_DATE={future_date}&TO_DATE={future_date}"
        page.goto(booking_url)
        # wait_for_page_to_load(logger, page, browser) this doesn't work?
        time.sleep(3)
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

            if "Reformer Pilates 60" in title and "16:30" in time:
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
                body="The class was not found on the booking page.",
            )

        browser.close()

import logging
import pathlib

from dotenv import load_dotenv

from book_class import book_gym_class
from credentials import get_user_credentials

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
BASE_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

if __name__ == "__main__":
    credentials = get_user_credentials()

    book_gym_class(
        credentials=credentials,
    )

from pydantic import BaseModel, SecretStr
import os

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


import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()


def get_secret(key: str) -> str:
    secret = os.getenv(key)

    if not secret:
        secret_name = f"{key}_file"
        path = os.getenv(secret_name.upper(), "")
        try:
            with open(path, "r") as file:
                return file.read().strip()
        except FileNotFoundError as e:
            raise Exception(f"Secret {secret_name} not found at {path}") from e
    return secret


db_user = get_secret("DB_USER")
db_password = get_secret("DB_PASSWORD")
db_host = get_secret("DB_HOST")
db_name = get_secret("DB_NAME")

quoted_user = quote_plus(db_user) if db_user else ""
quoted_password = quote_plus(db_password) if db_password else ""

db_url = make_url(
    f"postgresql+psycopg2://{quoted_user}:{quoted_password}@{db_host}/{db_name}"
)

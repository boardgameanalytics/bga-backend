"""
Configuration for all bga-backend services.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any


def get_secret(key: str, default: Any = None) -> str:
    """
    Load secret from environment variable. If none found, attempt to load from Docker secret.

    :param key: Name of the secret to load.
    :param default: Default value to return if secret not found.

    :return str: Secret value.
    """
    secret = os.getenv(key)

    if not secret:
        secret_name = f"{key}_file"
        if not (path := os.getenv(secret_name.upper())):
            return default
        try:
            with open(path, "r") as file:
                return file.read().strip()
        except FileNotFoundError as e:
            raise ValueError(f"Secret {secret_name} not found at {path}") from e
    return secret


# Database Connection
db_user = get_secret("DB_USER")
db_password = get_secret("DB_PASSWORD")
db_host = get_secret("DB_HOST")
db_name = get_secret("DB_NAME")

db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}"

# BoardGameGeek.com Login Credentials
bgg_username = get_secret("BGG_USERNAME")
bgg_password = get_secret("BGG_PASSWORD")

# Pipeline Configuration Options
data_path = Path(get_secret("DATA_PATH", "/data")) / datetime.now().strftime("%Y/%m/%d")
if _top_k_only := get_secret("TOP_K_ONLY"):
    top_k_only = int(_top_k_only)

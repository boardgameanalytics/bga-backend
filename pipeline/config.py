import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}"

bgg_username = os.getenv("BGG_USERNAME")
bgg_password = os.getenv("BGG_PASSWORD")

data_path = Path(os.getenv("DATA_PATH")) / datetime.now().strftime("%Y/%m/%d")

import html.parser
import zipfile
from http.client import HTTPException
from io import BytesIO
from pathlib import Path
from time import sleep

import requests

from src.pipeline import config
from src.pipeline.bggxmlapi2 import BggXmlApi2


def get_authenticated_session() -> requests.Session:
    """Create authenticated Requests session with BGG.com"""
    session = requests.Session()
    res = session.post(
        url="https://boardgamegeek.com/login/api/v1",
        json={
            "credentials": {
                "username": config.bgg_username,
                "password": config.bgg_password,
            }
        },
    )
    if res.status_code == 204:
        return session
    raise HTTPException(
        f"Authentication unsuccessful. Status code {res.status_code} returned."
    )


class S3LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.download_link = None
        self.current_tag = None
        self.looking_for_text = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            if "href" in attrs_dict:
                self.current_tag = attrs_dict["href"]
                self.looking_for_text = True

    def handle_data(self, data):
        if self.looking_for_text and data.strip() == "Click to Download":
            self.download_link = self.current_tag
            self.looking_for_text = False

    def handle_endtag(self, tag):
        if tag == "a" and self.looking_for_text:
            self.looking_for_text = False
            self.current_tag = None


def download_latest_rankings_dump(output_file_path: Path) -> Path:
    """
    Download the latest CSV of all games in database

    :param output_file_path: file to write output to
    """
    # Get link from page
    bg_ranks_page = get_authenticated_session().get(
        "https://boardgamegeek.com/data_dumps/bg_ranks"
    )
    parser = S3LinkParser()
    parser.feed(bg_ranks_page.text)
    download_url = parser.download_link

    if download_url is None:
        raise Exception("No download link found.")

    # Download and save to destination_path
    zip_buffer = requests.get(download_url)

    # Unzip
    output_file_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BytesIO(zip_buffer.content)) as zf:
        zf.extractall(output_file_path)

    return output_file_path


def extract_game_data(game_ids: list[str], destination_dir: Path) -> None:
    """
    Extract game data for all provided game IDs

    :param game_ids: list of game IDs
    :param destination_dir: Filepath of directory to save xml files
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    for num, xml in enumerate(BggXmlApi2.bulk_query_things(game_ids)):
        file_path = destination_dir / f"{str(num).zfill(4)}.xml"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(xml)
        sleep(5)

# mypy: disable-error-code="union-attr"

import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import pandas


def parse_description(desc: str) -> str:
    """Parse a description and replace escaped characters"""
    desc = re.sub(r"&rsquo;", "'", desc)
    desc = re.sub(r"&#.{,5};| {2,}", " ", desc)
    return desc.strip()


def parse_bgg_xml_to_dict(item: Element) -> dict[str, Any]:
    """
    Parse BoardGameGeek XML data and yield each game as a dictionary.

    :param item: BoardGameGeek XML data as string

    :return dict[str, Any]: XML game data as dictionary
    """

    item_ratings = item.find("statistics/ratings")
    game_id = item.get("id")

    if item is None or item_ratings is None or game_id is None:
        return {}

    return {
        "game": {
            "game_id": game_id,
            "type": item.get("type"),
            "name": item.find("name[@type='primary']").get("value"),
            "description": parse_description(item.findtext("description", default="")),
            "year_published": item.find("yearpublished").get("value"),
            "min_players": item.find("minplayers").get("value"),
            "max_players": item.find("maxplayers").get("value"),
            "playing_time": item.find("playingtime").get("value"),
            "min_playtime": item.find("minplaytime").get("value"),
            "max_playtime": item.find("maxplaytime").get("value"),
            "min_age": item.find("minage").get("value"),
            "total_ratings": item_ratings.find("usersrated").get("value"),
            "avg_rating": item_ratings.find("average").get("value"),
            "bayes_rating": item_ratings.find("bayesaverage").get("value"),
            "std_dev": item_ratings.find("stddev").get("value"),
            "owned_copies": item_ratings.find("owned").get("value"),
            "wishlist": item_ratings.find("wishing").get("value"),
            "total_weights": item_ratings.find("numweights").get("value"),
            "average_weight": item_ratings.find("averageweight").get("value"),
        },
        "links": [
            {
                "game_id": game_id,
                "link_type": link.get("type", default="").removeprefix("boardgame"),
                "link_id": link.get("id"),
                "link_name": link.get("value"),
            }
            for link in item.findall("link")
        ],
    }


def transform_xml_files(xml_dir: Path) -> dict[str, pandas.DataFrame]:
    """
    Transform XML game data to Pandas DataFrames

    :param xml_dir: Directory containing XML game data

    :return dict[str, pandas.DataFrame]: Dictionary of each separate dataset as a Pandas DataFrame
    """
    all_games = []
    all_links = []

    for xml_file in xml_dir.glob("*.xml"):
        tree = ElementTree.parse(xml_file)
        for item in tree.findall(".//item"):
            if item.get("id"):
                parsed_data = parse_bgg_xml_to_dict(item)
                all_games.append(parsed_data["game"])
                all_links.extend(parsed_data["links"])

    return {
        "games": pandas.DataFrame.from_records(all_games),
        "links": pandas.DataFrame.from_records(all_links),
    }


def save_processed_data(destination_dir: Path, **kwargs: pandas.DataFrame) -> None:
    """
    Save processed data to disk

    :param destination_dir: Directory to save processed data to
    :param kwargs: Pandas DataFrame arguments assigned to their name as the key
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    for filename, df in kwargs.items():
        df.to_csv(path_or_buf=destination_dir / f"{filename}.csv", index=False)

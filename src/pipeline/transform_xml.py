import logging
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import pandas


def find_and_get_value(element: Element, key: str) -> Any:
    """
    Find the value of a given key in the given element.

    :param element: Element to search in.
    :param key: Key to look for.

    :return Any: Value of the given key.
    """
    if sub_element := element.find(key):
        return sub_element.get("value")


def parse_description(desc: str) -> str:
    """Parse a description and replace escaped characters"""
    desc = re.sub(r"&rsquo;", "'", desc)
    desc = re.sub(r"&#.{,5};| {2,}", " ", desc)
    return desc.strip()


def parse_bgg_xml_to_dict(xml_element: Element) -> dict[str, Any]:
    """
    Parse BoardGameGeek XML data and return a dictionary of DataFrames.

    :param xml_element: BoardGameGeek XML data

    :return dict[str, Any]: XML game data as dictionary
    """
    if xml_element is None:
        return {}

    game_type = xml_element.findtext("type", default="")
    if game_type != "boardgame":
        return {}

    game_id = xml_element.get("id")
    if game_id is None:
        return {}

    ratings_element = xml_element.find("statistics/ratings")
    if ratings_element is None:
        return {}

    game_data = {
        "game_id": game_id,
        "title": find_and_get_value(xml_element, "name[@type='primary']"),
        "description": parse_description(
            xml_element.findtext("description", default="")
        ),
        "year_published": find_and_get_value(xml_element, "yearpublished"),
        "min_players": find_and_get_value(xml_element, "minplayers"),
        "max_players": find_and_get_value(xml_element, "maxplayers"),
        "playing_time": find_and_get_value(xml_element, "playingtime"),
        "min_playtime": find_and_get_value(xml_element, "minplaytime"),
        "max_playtime": find_and_get_value(xml_element, "maxplaytime"),
        "min_age": find_and_get_value(xml_element, "minage"),
        "total_ratings": find_and_get_value(ratings_element, "usersrated"),
        "avg_rating": find_and_get_value(ratings_element, "average"),
        "bayes_rating": find_and_get_value(ratings_element, "bayesaverage"),
        "std_dev_ratings": find_and_get_value(ratings_element, "stddev"),
        "owned_copies": find_and_get_value(ratings_element, "owned"),
        "wishlist": find_and_get_value(ratings_element, "wishing"),
        "total_weights": find_and_get_value(ratings_element, "numweights"),
        "average_weight": find_and_get_value(ratings_element, "averageweight"),
    }

    links_data = [
        {
            "game_id": game_id,
            "link_type": link.get("type", default="").removeprefix("boardgame"),
            "link_id": link.get("id"),
            "link_name": link.get("value"),
        }
        for link in xml_element.findall("link")
    ]

    return {"game": game_data, "links": links_data}


def separate_link_types(links_df: pandas.DataFrame) -> dict[str, pandas.DataFrame]:
    """
    Separate links DataFrame into separate dataframes for each link type.

    :param links_df: Links DataFrame

    :return dict[str, pandas.DataFrame]: Dictionary of link type DataFrames.
    """
    transformed_data = {}
    for name, df in links_df.drop_duplicates().groupby("link_type"):
        group_df = df.drop(columns="link_type").reset_index(drop=True)

        transformed_data[f"links/{name}_link"] = group_df.drop(
            columns=["link_name"]
        ).rename(columns={"link_id": f"{name}_id"})
        transformed_data[f"details/{name}_details"] = group_df.drop(
            columns=["game_id"]
        ).rename(columns={"link_id": f"{name}_id", "link_name": f"{name}_name"})

    return transformed_data


def transform_xml_files(xml_dir: Path) -> dict[str, pandas.DataFrame]:
    """
    Transform XML game data to Pandas DataFrames

    :param xml_dir: Directory containing XML game data

    :return dict[str, pandas.DataFrame]: Dictionary of each separate dataset as a Pandas DataFrame
    """
    all_games = []
    all_links = []

    for xml_file in xml_dir.glob("*.xml"):
        try:
            for item in ElementTree.parse(xml_file).findall(".//item"):
                if item.get("id"):
                    parsed_data = parse_bgg_xml_to_dict(item)
                    all_games.append(parsed_data["game"])
                    all_links.extend(parsed_data["links"])
        except ElementTree.ParseError as e:
            logging.error(f"Failed to parse {xml_file}: {e}")
            continue

    transformed_data = separate_link_types(pandas.DataFrame.from_records(all_links))
    transformed_data["details/game_details"] = pandas.DataFrame.from_records(all_games)

    return transformed_data


def save_processed_data(destination_dir: Path, **kwargs: pandas.DataFrame) -> None:
    """
    Save processed data to disk

    :param destination_dir: Directory to save processed data to
    :param kwargs: Pandas DataFrame arguments assigned to their name as the key
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    for filename, df in kwargs.items():
        df.to_csv(path_or_buf=destination_dir / f"{filename}.csv", index=False)


if __name__ == "__main__":
    transform_xml_files(Path("./data"))

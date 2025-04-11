import html
import logging
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from pandas import DataFrame


def find_and_get_value(element: Element, key: str) -> Any:
    """
    Find the value of a given key in the given element.

    :param element: Element to search in.
    :param key: Key to look for.

    :return Any: Value of the given key.
    """
    if element is None:
        return None

    sub_element = element.find(key)
    if sub_element is not None:
        return sub_element.get("value")


def parse_description(desc: str) -> str:
    """Parse a description and replace escaped characters"""
    if desc:
        desc = html.unescape(desc).replace("’", "'")
        desc = re.sub(r" {2,}", " ", desc)
        return desc.strip()
    else:
        return ""


def parse_bgg_xml_to_dict(xml_element: Element) -> dict[str, Any]:
    """
    Parse BoardGameGeek XML data and return a dictionary of DataFrames.

    :param xml_element: BoardGameGeek XML data

    :return dict[str, Any]: XML game data as dictionary
    """
    if not isinstance(xml_element, Element):
        raise TypeError(f"Expected XML element, got {type(xml_element)}")

    game_type = xml_element.get("type", default="")
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


def separate_link_types(links_df: DataFrame) -> dict[str, DataFrame]:
    """
    Separate links DataFrame into separate dataframes for each link type.

    :param links_df: Links DataFrame

    :return dict[str, DataFrame]: Dictionary of link type DataFrames.
    """
    if not isinstance(links_df, DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(links_df)}")

    transformed_data: dict = {}

    if links_df.empty:
        return transformed_data

    for name, df in links_df.drop_duplicates().groupby(by="link_type"):
        group_df = df.drop(columns="link_type").reset_index(drop=True)

        transformed_data[f"links/{name}_link"] = group_df.drop(
            columns=["link_name"]
        ).rename(columns={"link_id": f"{name}_id"})
        transformed_data[f"details/{name}_details"] = group_df.drop(
            columns=["game_id"]
        ).rename(columns={"link_id": f"{name}_id", "link_name": f"{name}_name"})

    return transformed_data


def transform_xml_files(xml_dir: Path) -> dict[str, DataFrame]:
    """
    Transform XML game data to Pandas DataFrames

    :param xml_dir: Directory containing XML game data

    :return dict[str, DataFrame]: Dictionary of each separate dataset as a Pandas DataFrame
    """
    if not isinstance(xml_dir, Path):
        raise TypeError(f"Expected Path, got {type(xml_dir)}")

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

    transformed_data = separate_link_types(DataFrame.from_records(all_links))
    game_details_df = DataFrame.from_records(all_games)
    if not game_details_df.empty:
        transformed_data["details/game_details"] = game_details_df

    return transformed_data


def save_df_to_csv(destination_dir: Path, **kwargs: DataFrame) -> None:
    """
    Save processed data to disk

    :param destination_dir: Directory to save processed data to
    :param kwargs: Pandas DataFrame arguments assigned to their name as the key
    """
    if not isinstance(destination_dir, Path):
        raise TypeError(f"Expected Path, got {type(destination_dir)}")

    destination_dir.mkdir(parents=True, exist_ok=True)
    for filename, df in kwargs.items():
        if not isinstance(df, DataFrame):
            raise AttributeError(f"Expected DataFrame, got {type(df)}")
        filepath = destination_dir / f"{filename}.csv"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path_or_buf=filepath, index=False)


if __name__ == "__main__":
    transform_xml_files(Path("./data"))

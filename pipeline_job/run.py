import logging
from datetime import datetime
from pathlib import Path

import pandas

from pipeline_job.extract import download_latest_rankings_dump, extract_game_data
from pipeline_job.transform_xml import save_processed_data, transform_xml_files

if __name__ == "__main__":
    root_path = Path("./data") / datetime.now().strftime("%Y/%m/%d")

    rankings_csv_path = root_path / "rankings_dumps"
    xml_dir = root_path / "xml"
    csv_dir = root_path / "csv"

    logging.info("Downloading latest ranking dump...")
    download_latest_rankings_dump(output_file_path=rankings_csv_path)
    game_id_list = pandas.read_csv(
        rankings_csv_path / "boardgames_ranks.csv", usecols=["id"]
    )["id"].tolist()
    logging.info(f"Found {len(game_id_list):,} games.")

    game_id_list = game_id_list[:10]  # ToDo: Remove limit before deployment

    logging.info(f"Extracting game data for {len(game_id_list):,} games...")
    extract_game_data(game_ids=game_id_list, destination_dir=xml_dir)

    logging.info("Transforming...")
    processed_dfs = transform_xml_files(xml_dir)
    save_processed_data(destination_dir=csv_dir, **processed_dfs)

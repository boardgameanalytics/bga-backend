import logging

import pandas

from src.pipeline import config
from src.pipeline.extract import download_latest_rankings_dump, extract_game_data
from src.pipeline.load import load_csv_files_into_db
from src.pipeline.transform_xml import save_processed_data, transform_xml_files

if __name__ == "__main__":
    logging.info("--Starting job--")

    rankings_csv_path = config.data_path / "rankings_dumps"
    xml_dir = config.data_path / "xml"
    csv_dir = config.data_path / "csv"

    logging.info("Downloading latest ranking dump...")
    download_latest_rankings_dump(output_file_path=rankings_csv_path)
    game_id_list = pandas.read_csv(
        rankings_csv_path / "boardgames_ranks.csv", usecols=["id"]
    )["id"].tolist()
    logging.info(f"Found {len(game_id_list):,} games in rankings dump.")

    if config.top_k_only > 0:
        logging.info(f"Limiting extraction to the top {config.top_k_only} games.")
        game_id_list = game_id_list[: config.top_k_only]

    logging.info("Extracting game data from BGG API...")
    extract_game_data(game_ids=game_id_list, destination_dir=xml_dir)

    logging.info("Transforming...")
    processed_dfs = transform_xml_files(xml_dir)
    save_processed_data(destination_dir=csv_dir, **processed_dfs)

    logging.info("Loading...")
    load_csv_files_into_db(csv_dir)
    logging.info("Loading complete.")

    logging.info("--Job Complete--")

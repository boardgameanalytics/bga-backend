import logging

import pandas
from common import config  # type: ignore
from pipeline.extract import (  # type: ignore
    download_latest_rankings_dump,
    extract_game_data,
)
from pipeline.load import load_csv_files_into_db  # type: ignore
from pipeline.transform_xml import (  # type: ignore
    save_df_to_csv,
    transform_xml_files,
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
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

    if config.top_k_only:
        logging.info(f"Limiting extraction to the top {config.top_k_only} games.")
        game_id_list = game_id_list[: config.top_k_only]

    logging.info("Extracting game data from BGG API...")
    extract_game_data(game_ids=game_id_list, destination_dir=xml_dir)

    logging.info("Transforming...")
    processed_dfs = transform_xml_files(xml_dir)
    save_df_to_csv(destination_dir=csv_dir, **processed_dfs)

    logging.info("Loading...")
    load_csv_files_into_db(csv_dir)
    logging.info("Loading complete.")

    logging.info("--Job Complete--")

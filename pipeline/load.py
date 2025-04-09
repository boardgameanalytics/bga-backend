import logging
from itertools import chain
from pathlib import Path

import pandas
from sqlalchemy import create_engine

from pipeline import config


def load_csv_files_into_db(csv_base_dir: Path) -> None:
    """
    Load contents of all CSV files into SQL database table.
    Loads CSV files from details and links subdirectories, respectively.

    :param csv_base_dir: Path of CSV base directory
    """
    engine = create_engine(config.db_url)

    csv_files = chain(
        (csv_base_dir / "details").glob("*.csv"),
        (csv_base_dir / "links").glob("*.csv"),
    )

    for csv_file in csv_files:
        table_name = csv_file.stem
        logging.info(f"Loading {csv_file.name} into table {table_name}...")
        try:
            table_df = pandas.read_csv(csv_file)
            table_df.to_sql(
                name=table_name, con=engine, if_exists="replace", index=False
            )
        except Exception as e:
            logging.error(f"Error loading {csv_file.name}: {e}")

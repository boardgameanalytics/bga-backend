from pathlib import Path
from typing import Any

import pandas


def load_table(csv_path: Path, engine: Any) -> None:
    """
    Load contents of CSV file into SQL database table

    :param csv_path: Path of CSV file to load into table
    :param engine: DB connection object
    """
    table_name = csv_path.stem
    table_df = pandas.read_csv(csv_path, header=0)
    table_df.to_sql(name=table_name, con=engine)  # , if_exists="append")

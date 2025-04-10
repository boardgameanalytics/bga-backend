import logging
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pytest_mock import MockerFixture
from sqlalchemy import create_engine

from src.pipeline import config
from src.pipeline.load import load_csv_files_into_db


class TestLoadCsvFilesIntoDb:
    @pytest.mark.parametrize(
        "csv_files",
        [
            (
                {
                    "details": [
                        (
                            "game_details",
                            pd.DataFrame({"id": [1, 2], "name": ["Game 1", "Game 2"]}),
                        )
                    ],
                    "links": [
                        (
                            "category_link",
                            pd.DataFrame({"game_id": [1], "category_id": [10]}),
                        )
                    ],
                }
            ),  # happy_path_multiple_files
            ({"details": [], "links": []}),  # edge_case_no_files
        ],
        ids=["happy_path_multiple_files", "edge_case_no_files"],
    )
    def test_load_csv_files_into_db(
        self,
        csv_files: dict[str, list[tuple[str, pd.DataFrame]]],
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        # Arrange
        csv_base_dir = tmp_path / "csv_files"
        csv_base_dir.mkdir()
        (csv_base_dir / "details").mkdir()
        (csv_base_dir / "links").mkdir()

        for subdir, files in csv_files.items():
            for filename, df in files:
                df.to_csv(csv_base_dir / subdir / f"{filename}.csv", index=False)

        mock_engine = mocker.MagicMock(spec=create_engine(config.db_url))
        mocker.patch("src.pipeline.load.create_engine", return_value=mock_engine)
        mock_to_sql = mocker.patch("pandas.DataFrame.to_sql")

        # Act
        load_csv_files_into_db(csv_base_dir)

        # Assert
        expected_calls: list = []
        for files in csv_files.values():
            expected_calls.extend(
                mocker.call(
                    name=filename,
                    con=mock_engine,
                    if_exists="replace",
                    index=False,
                )
                for filename, df in files
            )
        mock_to_sql.assert_has_calls(expected_calls, any_order=True)

    @pytest.mark.parametrize(
        "csv_files, expected_log_message",
        [
            (
                {
                    "details": [
                        (
                            "game_details",
                            pd.DataFrame({"id": [1, 2], "name": ["Game 1", "Game 2"]}),
                        )
                    ],
                    "links": [
                        (
                            "category_link",
                            pd.DataFrame({"game_id": [1], "category_id": [10]}),
                        )
                    ],
                },
                "Error loading game_details.csv",
            ),  # error_during_csv_load
        ],
        ids=["error_during_csv_load"],
    )
    def test_load_csv_files_into_db_error_handling(
        self,
        csv_files: dict[str, list[tuple[str, pd.DataFrame]]],
        expected_log_message: str,
        tmp_path: Path,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ):
        # Arrange
        csv_base_dir = tmp_path / "csv_files"
        csv_base_dir.mkdir()
        (csv_base_dir / "details").mkdir()
        (csv_base_dir / "links").mkdir()

        for subdir, files in csv_files.items():
            for filename, df in files:
                df.to_csv(csv_base_dir / subdir / f"{filename}.csv", index=False)

        mock_engine = mocker.MagicMock(spec=create_engine(config.db_url))
        mocker.patch("src.pipeline.load.create_engine", return_value=mock_engine)

        # Simulate an error during DataFrame loading
        mocker.patch("pandas.read_csv", side_effect=Exception("Mock CSV read error"))

        # Act
        with caplog.at_level(logging.ERROR):
            load_csv_files_into_db(csv_base_dir)

        # Assert
        assert expected_log_message in caplog.text

    @pytest.mark.parametrize(
        "csv_base_dir, expected_exception",
        [(123, TypeError)],  # type: ignore[arg-type] # error_invalid_csv_base_dir_type
        ids=["error_invalid_csv_base_dir_type"],
    )
    def test_load_csv_files_into_db_error_cases(
        self, csv_base_dir: Any, expected_exception: type[Exception]
    ):
        with pytest.raises(expected_exception):
            load_csv_files_into_db(csv_base_dir)

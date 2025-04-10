import logging
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import fromstring

import pytest
from pandas import DataFrame, read_csv
from pandas import testing as pd_testing
from pytest_mock import MockerFixture

from src.pipeline.transform_xml import (
    find_and_get_value,
    parse_bgg_xml_to_dict,
    parse_description,
    save_processed_data,
    separate_link_types,
    transform_xml_files,
)


class TestFindAndGetValue:
    @pytest.mark.parametrize(
        "xml_string, key, expected_value",
        [
            ("<data><item value='1'/></data>", "item", "1"),  # happy_path_simple
            (
                "<data><item key='other' value='2'/></data>",
                "item",
                "2",
            ),  # happy_path_other_attributes
            (
                "<data><a><b><c value='3'/></b></a></data>",
                "a/b/c",
                "3",
            ),  # happy_path_nested
        ],
        ids=["happy_path_simple", "happy_path_other_attributes", "happy_path_nested"],
    )
    def test_find_and_get_value_happy_path(
        self, xml_string: str, key: str, expected_value: str
    ):
        # Arrange
        element = fromstring(xml_string)

        # Act
        value = find_and_get_value(element, key)

        # Assert
        assert value == expected_value

    @pytest.mark.parametrize(
        "xml_string, key, expected_value",
        [
            ("<data></data>", "item", None),  # edge_case_missing_key
            ("<data><item/></data>", "item", None),  # edge_case_missing_value_attribute
            (
                "<data><item value=''/></data>",
                "item",
                "",
            ),  # edge_case_empty_value_attribute
        ],
        ids=[
            "edge_case_missing_key",
            "edge_case_missing_value_attribute",
            "edge_case_empty_value_attribute",
        ],
    )
    def test_find_and_get_value_edge_cases(
        self, xml_string: str, key: str, expected_value: str | None
    ):
        # Arrange
        element = fromstring(xml_string)

        # Act
        value = find_and_get_value(element, key)

        # Assert
        assert value == expected_value


class TestParseDescription:
    @pytest.mark.parametrize(
        "desc, expected_desc",
        [
            (
                "This is a simple description.",
                "This is a simple description.",
            ),  # happy_path_simple
            (
                "Description with &rsquo;escaped&rsquo; characters.",
                "Description with 'escaped' characters.",
            ),
            # happy_path_escaped_chars
            (
                "Description with &#12345; HTML entities.",
                "Description with 〹 HTML entities.",
            ),
            # happy_path_html_entities
            (
                "Description with   multiple    spaces.",
                "Description with multiple spaces.",
            ),
            # happy_path_multiple_spaces
            (
                "Description with &rsquo;escaped&rsquo; characters and &#123; HTML entities.",
                "Description with 'escaped' characters and { HTML entities.",
            ),  # happy_path_combined
            (
                "  Description with leading and trailing spaces.   ",
                "Description with leading and trailing spaces.",
            ),  # happy_path_leading_trailing_spaces
        ],
        ids=[
            "happy_path_simple",
            "happy_path_escaped_chars",
            "happy_path_html_entities",
            "happy_path_multiple_spaces",
            "happy_path_combined",
            "happy_path_leading_trailing_spaces",
        ],
    )
    def test_parse_description_happy_path(self, desc: str, expected_desc: str):
        # Act
        parsed_desc = parse_description(desc)

        # Assert
        assert parsed_desc == expected_desc

    @pytest.mark.parametrize(
        "desc, expected_desc",
        [
            ("", ""),  # edge_case_empty_string
            ("   ", ""),  # edge_case_only_spaces
        ],
        ids=["edge_case_empty_string", "edge_case_only_spaces"],
    )
    def test_parse_description_edge_cases(self, desc: str | None, expected_desc: str):
        # Act
        parsed_desc = parse_description(desc)  # type: ignore[arg-type]

        # Assert
        assert parsed_desc == expected_desc

    @pytest.mark.parametrize(
        "desc, expected_exception",
        [(123, TypeError)],  # type: ignore[arg-type] # error_invalid_input_type
        ids=["error_invalid_input_type"],
    )
    def test_parse_description_error_cases(
        self, desc: Any, expected_exception: type[Exception]
    ):
        with pytest.raises(expected_exception):
            parse_description(desc)


class TestParseBggXmlToDict:
    @pytest.mark.parametrize(
        "xml_string, expected_dict",
        [
            (
                """<item type="boardgame" id="1">
                        <name type="primary" value="Game 1"/>
                        <description>Description 1</description>
                        <yearpublished value="2020"/>
                        <minplayers value="2"/>
                        <maxplayers value="4"/>
                        <playingtime value="60"/>
                        <minplaytime value="30"/>
                        <maxplaytime value="90"/>
                        <minage value="10"/>
                        <statistics>
                            <ratings>
                                <usersrated value="100"/>
                                <average value="7.5"/>
                                <bayesaverage value="7.2"/>
                                <stddev value="1.2"/>
                                <owned value="200"/>
                                <wishing value="50"/>
                                <numweights value="30"/>
                                <averageweight value="2.5"/>
                            </ratings>
                        </statistics>
                        <link type="boardgamecategory" id="1000" value="Category 1"/>
                        <link type="boardgamemechanic" id="2000" value="Mechanic 1"/>
                    </item>""",
                {
                    "game": {
                        "game_id": "1",
                        "title": "Game 1",
                        "description": "Description 1",
                        "year_published": "2020",
                        "min_players": "2",
                        "max_players": "4",
                        "playing_time": "60",
                        "min_playtime": "30",
                        "max_playtime": "90",
                        "min_age": "10",
                        "total_ratings": "100",
                        "avg_rating": "7.5",
                        "bayes_rating": "7.2",
                        "std_dev_ratings": "1.2",
                        "owned_copies": "200",
                        "wishlist": "50",
                        "total_weights": "30",
                        "average_weight": "2.5",
                    },
                    "links": [
                        {
                            "game_id": "1",
                            "link_type": "category",
                            "link_id": "1000",
                            "link_name": "Category 1",
                        },
                        {
                            "game_id": "1",
                            "link_type": "mechanic",
                            "link_id": "2000",
                            "link_name": "Mechanic 1",
                        },
                    ],
                },
            ),  # happy_path_complete_data
            (
                """<item type="boardgame" id="2"></item>""",
                {},
            ),  # happy_path_minimal_data
        ],
        ids=["happy_path_complete_data", "happy_path_minimal_data"],
    )
    def test_parse_bgg_xml_to_dict_happy_path(
        self, xml_string: str, expected_dict: dict[str, Any]
    ):
        # Arrange
        xml_element = fromstring(xml_string)

        # Act
        result = parse_bgg_xml_to_dict(xml_element)

        # Assert
        assert result == expected_dict

    @pytest.mark.parametrize(
        "xml_string, expected_dict",
        [
            ("<item type='videogame' id='3'></item>", {}),  # edge_case_wrong_type
            ("<item id='4'></item>", {}),  # edge_case_no_type
            ("<item type='boardgame'></item>", {}),  # edge_case_no_id
            (
                "<item type='boardgame' id='6'><statistics></statistics></item>",
                {},
            ),  # edge_case_no_ratings
        ],
        ids=[
            "edge_case_wrong_type",
            "edge_case_no_type",
            "edge_case_no_id",
            "edge_case_no_ratings",
        ],
    )
    def test_parse_bgg_xml_to_dict_edge_cases(
        self, xml_string: str | None, expected_dict: dict[str, Any]
    ):
        # Arrange
        xml_element = fromstring(xml_string) if xml_string else None

        # Act
        result = parse_bgg_xml_to_dict(xml_element)  # type: ignore

        # Assert
        assert result == expected_dict

    @pytest.mark.parametrize(
        "xml_element, expected_exception",
        [
            (123, TypeError),  # type: ignore[arg-type] # error_invalid_input_type
        ],
        ids=["error_invalid_input_type"],
    )
    def test_parse_bgg_xml_to_dict_error_cases(
        self, xml_element: Any, expected_exception: type[Exception]
    ):
        # Act & Assert
        with pytest.raises(expected_exception):
            parse_bgg_xml_to_dict(xml_element)


class TestSeparateLinkTypes:
    @pytest.mark.parametrize(
        "links_df, expected_data",
        [
            (
                DataFrame(
                    {
                        "game_id": ["1", "1", "2", "2"],
                        "link_type": ["category", "mechanic", "category", "artist"],
                        "link_id": ["100", "200", "100", "300"],
                        "link_name": [
                            "Category 1",
                            "Mechanic 1",
                            "Category 1",
                            "Artist 1",
                        ],
                    }
                ),
                {
                    "links/category_link": DataFrame(
                        {"game_id": ["1", "2"], "category_id": ["100", "100"]}
                    ),
                    "details/category_details": DataFrame(
                        {
                            "category_id": ["100", "100"],
                            "category_name": ["Category 1", "Category 1"],
                        }
                    ),
                    "links/mechanic_link": DataFrame(
                        {"game_id": ["1"], "mechanic_id": ["200"]}
                    ),
                    "details/mechanic_details": DataFrame(
                        {"mechanic_id": ["200"], "mechanic_name": ["Mechanic 1"]}
                    ),
                    "links/artist_link": DataFrame(
                        {"game_id": ["2"], "artist_id": ["300"]}
                    ),
                    "details/artist_details": DataFrame(
                        {"artist_id": ["300"], "artist_name": ["Artist 1"]}
                    ),
                },
            ),  # happy_path_multiple_link_types
            (
                DataFrame(
                    {
                        "game_id": ["1", "1"],
                        "link_type": ["category", "category"],
                        "link_id": ["100", "100"],
                        "link_name": ["Category 1", "Category 1"],
                    }
                ),
                {
                    "links/category_link": DataFrame(
                        {"game_id": ["1"], "category_id": ["100"]}
                    ),
                    "details/category_details": DataFrame(
                        {"category_id": ["100"], "category_name": ["Category 1"]}
                    ),
                },
            ),  # happy_path_single_link_type
        ],
        ids=["happy_path_multiple_link_types", "happy_path_single_link_type"],
    )
    def test_separate_link_types_happy_path(
        self, links_df: DataFrame, expected_data: dict[str, DataFrame]
    ):
        # Act
        transformed_data = separate_link_types(links_df)

        # Assert
        assert transformed_data.keys() == expected_data.keys()
        for key in transformed_data:
            pd_testing.assert_frame_equal(transformed_data[key], expected_data[key])

    @pytest.mark.parametrize(
        "links_df, expected_data",
        [
            (
                DataFrame(
                    {"game_id": [], "link_type": [], "link_id": [], "link_name": []}
                ),
                {},
            ),  # edge_case_empty_df
        ],
        ids=["edge_case_empty_df"],
    )
    def test_separate_link_types_edge_cases(
        self, links_df: DataFrame, expected_data: dict[str, DataFrame]
    ):
        # Act
        transformed_data = separate_link_types(links_df)

        # Assert
        assert transformed_data == expected_data

    @pytest.mark.parametrize(
        "links_df, expected_exception",
        [
            (
                DataFrame(
                    {"game_id": ["1"], "link_id": ["100"], "link_name": ["Name"]}
                ),
                KeyError,
            ),  # error_missing_link_type
            (123, TypeError),  # type: ignore[arg-type] # error_invalid_input_type
        ],
        ids=["error_missing_link_type", "error_invalid_input_type"],
    )
    def test_separate_link_types_error_cases(
        self, links_df: DataFrame | Any, expected_exception: type[Exception]
    ):
        # Act & Assert
        with pytest.raises(expected_exception):
            separate_link_types(links_df)


class TestTransformXmlFiles:
    @pytest.mark.parametrize(
        "xml_files, expected_data",
        [
            (
                [
                    """<data><items>
                    <item type="boardgame" id="1">
                        <name type="primary" value="Game 1"/>
                        <link type="boardgamecategory" id="100" value="Category 1"/>
                        <statistics><ratings></ratings></statistics>
                    </item>
                    <item type="boardgame" id="2">
                        <name type="primary" value="Game 2"/>
                        <link type="boardgamemechanic" id="200" value="Mechanic 1"/>
                        <statistics><ratings></ratings></statistics>
                    </item>
                    </items></data>""",
                    """<data><items>
                    <item type="boardgame" id="3">
                        <name type="primary" value="Game 3"/>
                        <statistics><ratings></ratings></statistics>
                    </item>
                  </items></data>""",
                ],
                {
                    "details/game_details": DataFrame(
                        {
                            "game_id": ["1", "2", "3"],
                            "title": ["Game 1", "Game 2", "Game 3"],
                            "description": ["", "", ""],
                            "year_published": [None, None, None],
                            "min_players": [None, None, None],
                            "max_players": [None, None, None],
                            "playing_time": [None, None, None],
                            "min_playtime": [None, None, None],
                            "max_playtime": [None, None, None],
                            "min_age": [None, None, None],
                            "total_ratings": [None, None, None],
                            "avg_rating": [None, None, None],
                            "bayes_rating": [None, None, None],
                            "std_dev_ratings": [None, None, None],
                            "owned_copies": [None, None, None],
                            "wishlist": [None, None, None],
                            "total_weights": [None, None, None],
                            "average_weight": [None, None, None],
                        }
                    ),
                    "links/category_link": DataFrame(
                        {"game_id": ["1"], "category_id": ["100"]}
                    ),
                    "details/category_details": DataFrame(
                        {"category_id": ["100"], "category_name": ["Category 1"]}
                    ),
                    "links/mechanic_link": DataFrame(
                        {"game_id": ["2"], "mechanic_id": ["200"]}
                    ),
                    "details/mechanic_details": DataFrame(
                        {"mechanic_id": ["200"], "mechanic_name": ["Mechanic 1"]}
                    ),
                },
            ),  # happy_path_multiple_files
            ([], {}),  # edge_case_no_files
        ],
        ids=["happy_path_multiple_files", "edge_case_no_files"],
    )
    def test_transform_xml_files(
        self,
        xml_files: list[str],
        expected_data: dict[str, DataFrame],
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        # Arrange
        xml_dir = tmp_path / "xml_files"
        xml_dir.mkdir()
        for i, xml_string in enumerate(xml_files):
            (xml_dir / f"0{i}.xml").write_text(xml_string, encoding="utf-8")

        mocker.patch("src.pipeline.transform_xml.logging.error")

        # Act
        transformed_data = transform_xml_files(xml_dir)

        # Assert
        assert transformed_data.keys() == expected_data.keys()
        for key in transformed_data:
            pd_testing.assert_frame_equal(
                transformed_data[key], expected_data[key], check_dtype=False
            )

    @pytest.mark.parametrize(
        "xml_files",
        [
            [
                "<invalid_xml",  # edge_case_invalid_xml
            ]
        ],
        ids=["edge_case_invalid_xml"],
    )
    def test_transform_xml_files_invalid_xml(
        self,
        xml_files: list[str],
        tmp_path: Path,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ):
        # Arrange
        xml_dir = tmp_path / "xml_files"
        xml_dir.mkdir()
        for i, xml_string in enumerate(xml_files):
            (xml_dir / f"{i}.xml").write_text(xml_string, encoding="utf-8")

        # Act
        with caplog.at_level(logging.ERROR):
            transformed_data = transform_xml_files(xml_dir)

        # Assert
        assert transformed_data == {}
        assert "Failed to parse" in caplog.text

    @pytest.mark.parametrize(
        "xml_dir, expected_exception",
        [
            (123, TypeError),  # type: ignore[arg-type] # error_invalid_xml_dir_type
        ],
        ids=["error_invalid_xml_dir_type"],
    )
    def test_transform_xml_files_error_cases(
        self, xml_dir: Any, expected_exception: type[Exception]
    ):
        # Act & Assert
        with pytest.raises(expected_exception):
            transform_xml_files(xml_dir)


class TestSaveProcessedData:
    @pytest.mark.parametrize(
        "dataframes",
        [
            (
                {
                    "df1": DataFrame({"col1": [1, 2], "col2": [3, 4]}),
                    "df2": DataFrame({"col3": [5, 6]}),
                }
            ),
            # happy_path_multiple_dataframes
            ({"df1": DataFrame({"col1": [1]})}),  # happy_path_single_dataframe
        ],
        ids=["happy_path_multiple_dataframes", "happy_path_single_dataframe"],
    )
    def test_save_processed_data_happy_path(
        self, dataframes: dict[str, DataFrame], tmp_path: Path
    ):
        # Arrange
        destination_dir = tmp_path / "data"

        # Act
        save_processed_data(destination_dir, **dataframes)

        # Assert
        assert destination_dir.exists()
        for filename, df in dataframes.items():
            filepath = destination_dir / f"{filename}.csv"
            assert filepath.exists()
            read_df = read_csv(filepath)
            pd_testing.assert_frame_equal(df, read_df)

    @pytest.mark.parametrize(
        "dataframes",
        [
            ({}),  # edge_case_no_dataframes
        ],
        ids=["edge_case_no_dataframes"],
    )
    def test_save_processed_data_edge_cases(
        self, dataframes: dict[str, DataFrame], tmp_path: Path
    ):
        # Arrange
        destination_dir = tmp_path / "data"

        # Act
        save_processed_data(destination_dir, **dataframes)

        # Assert
        assert destination_dir.exists()

    @pytest.mark.parametrize(
        "destination_dir, dataframes, expected_exception",
        [
            (123, {"df1": DataFrame({"col1": [1]})}, TypeError),
            # type: ignore[arg-type] # error_invalid_destination_type
            (Path("./invalid/path"), {"df1": 123}, AttributeError),
            # type: ignore[dict-item] # error_invalid_dataframe_type
        ],
        ids=["error_invalid_destination_type", "error_invalid_dataframe_type"],
    )
    def test_save_processed_data_error_cases(
        self,
        destination_dir: Path | Any,
        dataframes: dict[str, DataFrame | Any],
        expected_exception: type[Exception],
    ):
        # Act & Assert
        with pytest.raises(expected_exception):
            save_processed_data(destination_dir, **dataframes)

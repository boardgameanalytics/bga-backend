import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from requests import Response, Session

from src.pipeline import config
from src.pipeline.bggxmlapi2 import BggXmlApi2
from src.pipeline.extract import (
    S3LinkParser,
    download_latest_rankings_dump,
    extract_game_data,
    get_authenticated_session,
)


class TestGetAuthenticatedSession:
    @pytest.mark.parametrize(
        "status_code",
        [204],
        ids=["happy_path"],
    )
    def test_get_authenticated_session_happy_path(
        self, status_code: int, mocker: MockerFixture
    ):
        # Arrange
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = status_code

        mock_post = mocker.patch("requests.Session.post", return_value=mock_response)

        # Act
        session = get_authenticated_session()

        # Assert
        assert isinstance(session, Session)
        mock_post.assert_called_once_with(
            url="https://boardgamegeek.com/login/api/v1",
            json={
                "credentials": {
                    "username": config.bgg_username,
                    "password": config.bgg_password,
                }
            },
        )

    @pytest.mark.parametrize(
        "status_code, expected_exception_message",
        [
            (401, "Authentication unsuccessful. Status code 401 returned."),
            (500, "Authentication unsuccessful. Status code 500 returned."),
        ],
        ids=["error_401", "error_500"],
    )
    def test_get_authenticated_session_error_cases(
        self, status_code: int, expected_exception_message: str, mocker: MockerFixture
    ):
        # Arrange
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = status_code

        mocker.patch("requests.Session.post", return_value=mock_response)

        # Act & Assert
        with pytest.raises(Exception) as e:
            get_authenticated_session()
        assert str(e.value) == expected_exception_message


class TestS3LinkParser:
    @pytest.mark.parametrize(
        "html, expected_link",
        [
            (
                '<a href="https://example.com/download">Click to Download</a>',
                "https://example.com/download",
            ),  # happy_path_simple_link
            (
                '<a href="https://another-example.com/file.zip">Click to Download</a>',
                "https://another-example.com/file.zip",
            ),  # happy_path_link_with_file_extension
            (
                """<a
                            href="https://long-link.com/path/to/download"
                            >Click to Download</a>""",
                "https://long-link.com/path/to/download",
            ),  # happy_path_long_link_with_formatting
            (
                '<a href="invalid-link"> Not Click to Download</a>',
                None,
            ),  # edge_case_wrong_text
            ("<a>Click to Download</a>", None),  # edge_case_no_href
            ("", None),  # edge_case_empty_html
            (
                '<a href="link1">Click to Download</a><a href="link2">Something else</a>',
                "link1",
            ),  # edge_case_multiple_links
        ],
        ids=[
            "happy_path_simple_link",
            "happy_path_link_with_file_extension",
            "happy_path_long_link_with_formatting",
            "edge_case_wrong_text",
            "edge_case_no_href",
            "edge_case_empty_html",
            "edge_case_multiple_links",
        ],
    )
    def test_s3_link_parser(self, html: str, expected_link: str | None):
        # Arrange
        parser = S3LinkParser()

        # Act
        parser.feed(html)

        # Assert
        assert parser.download_link == expected_link


class TestDownloadLatestRankingsDump:
    @pytest.mark.parametrize(
        "mock_html, mock_zip_content, expected_files",
        [
            (
                '<a href="https://example.com/bg_ranks.zip">Click to Download</a>',
                b"zip file contents",
                ["boardgames_ranks.csv"],
            )
        ],
        ids=["happy_path"],
    )
    def test_download_latest_rankings_dump_happy_path(
        self,
        mock_html: str,
        mock_zip_content: bytes,
        expected_files: list[str],
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # Arrange
        mock_bg_ranks_page_response = mocker.Mock(spec=Response)
        mock_bg_ranks_page_response.text = mock_html

        mock_get_authenticated_session = mocker.patch(
            "src.pipeline.extract.get_authenticated_session",
            return_value=mocker.Mock(spec=Session),
        )
        mock_get_authenticated_session.return_value.get.return_value = (
            mock_bg_ranks_page_response
        )

        mock_zip_response = mocker.Mock(spec=Response)
        mock_zip_response.content = mock_zip_content
        mocker.patch("requests.get", return_value=mock_zip_response)

        output_file_path = tmp_path / "bg_ranks"

        # Create dummy zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for file in expected_files:
                zf.writestr(file, "dummy content")
        zip_buffer.seek(0)
        mock_zip_response.content = zip_buffer.read()

        # Act
        download_latest_rankings_dump(output_file_path=output_file_path)

        # Assert
        mock_get_authenticated_session.assert_called_once()
        mock_get_authenticated_session.return_value.get.assert_called_once_with(
            "https://boardgamegeek.com/data_dumps/bg_ranks"
        )

        for file in expected_files:
            assert (output_file_path / file).exists()

    @pytest.mark.parametrize(
        "mock_html, expected_exception_message",
        [
            (
                "<html></html>",
                "No download link found.",
            ),  # error_no_download_link
        ],
        ids=["error_no_download_link"],
    )
    def test_download_latest_rankings_dump_error_cases(
        self,
        mock_html: str,
        expected_exception_message: str,
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # Arrange
        mock_bg_ranks_page_response = mocker.Mock(spec=Response)
        mock_bg_ranks_page_response.text = mock_html

        mock_session = mocker.Mock(spec=Session)
        mock_session.get.return_value = mock_bg_ranks_page_response
        mocker.patch(
            "src.pipeline.extract.get_authenticated_session", return_value=mock_session
        )

        mock_zip_response = mocker.Mock(spec=Response)
        mock_zip_response.status_code = 401  # Simulate authentication failure
        mocker.patch(
            "src.pipeline.extract.requests.get", return_value=mock_zip_response
        )

        output_file_path = tmp_path / "bg_ranks"

        # Act & Assert
        with pytest.raises(Exception) as e:
            download_latest_rankings_dump(output_file_path=output_file_path)
        assert str(e.value) == expected_exception_message


class TestExtractGameData:
    @pytest.mark.parametrize(
        "game_ids, mock_xml_responses",
        [
            (
                ["1", "2", "3"],
                ["<xml>Game 1</xml>", "<xml>Game 2</xml>", "<xml>Game 3</xml>"],
            ),
            # happy_path_multiple_games
            (["1"], ["<xml>Game 1</xml>"]),  # happy_path_single_game
        ],
        ids=["happy_path_multiple_games", "happy_path_single_game"],
    )
    def test_extract_game_data_happy_path(
        self,
        game_ids: list[str],
        mock_xml_responses: list[str],
        mocker: MockerFixture,
        tmp_path: Path,
    ):
        # Arrange
        destination_dir = tmp_path / "game_data"
        mocker.patch(
            "src.pipeline.bggxmlapi2.BggXmlApi2.bulk_query_things",
            return_value=mock_xml_responses,
        )
        mock_sleep = mocker.patch("src.pipeline.extract.sleep")

        # Act
        extract_game_data(game_ids, destination_dir)

        # Assert
        BggXmlApi2.bulk_query_things.assert_called_once_with(game_ids)  # type: ignore
        mock_sleep.assert_called_with(5)
        assert destination_dir.exists()
        for i, xml in enumerate(mock_xml_responses):
            file_path = destination_dir / f"{str(i).zfill(4)}.xml"
            assert file_path.exists()
            with open(file_path, "r", encoding="utf-8") as f:
                assert f.read() == xml

    def test_extract_game_data_empty_list_edge_case(
        self, mocker: MockerFixture, tmp_path: Path
    ):
        # Arrange
        destination_dir = tmp_path / "game_data"
        mocker.patch(
            "src.pipeline.bggxmlapi2.BggXmlApi2.bulk_query_things", return_value=[]
        )

        # Act
        extract_game_data([], destination_dir)

        # Assert
        BggXmlApi2.bulk_query_things.assert_called_once_with([])  # type: ignore
        assert destination_dir.exists()

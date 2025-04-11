import pytest
from pytest_mock import MockerFixture
from requests import Response

from services.pipeline.bggxmlapi2 import BggXmlApi2


class TestBuildQueryURL:
    base_url = "https://boardgamegeek.com/xmlapi2"

    @pytest.mark.parametrize(
        "query_type, params, expected_url",
        [
            (
                "thing",
                {"id": "123", "stats": "1"},
                f"{base_url}/thing?id=123&stats=1",
            ),  # happy_path_thing_query
            (
                "user",
                {"name": "johndoe", "buddies": "1"},
                f"{base_url}/user?name=johndoe&buddies=1",
            ),  # happy_path_user_query
            (
                "search",
                {"query": "Catan", "type": "boardgame"},
                f"{base_url}/search?query=Catan&type=boardgame",
            ),  # happy_path_search_query
            (
                "thing",
                {},
                f"{base_url}/thing?",
            ),  # edge_case_empty_params
            (
                "collections",
                {"username": "testuser", "own": "1"},
                f"{base_url}/collections?username=testuser&own=1",
            ),  # happy_path_collections_query
            (
                "thing",
                {"id": "123", "invalidparam": "value"},
                f"{base_url}/thing?id=123&invalidparam=value",
            ),  # edge_case_invalid_param
        ],
        ids=[
            "happy_path_thing_query",
            "happy_path_user_query",
            "happy_path_search_query",
            "edge_case_empty_params",
            "happy_path_collections_query",
            "edge_case_invalid_param",
        ],
    )
    def test_build_query_url_happy_path(self, query_type, params, expected_url):
        # Act
        actual_url = BggXmlApi2._build_query_url(query_type, params)

        # Assert
        assert actual_url == expected_url


class TestSegmentList:
    @pytest.mark.parametrize(
        "item_list, batch_size, expected_segments",
        [
            (
                list(range(100)),
                20,
                [list(range(i, min(i + 20, 100))) for i in range(0, 100, 20)],
            ),  # happy_path_even_division
            (
                list(range(35)),
                10,
                [list(range(i, min(i + 10, 35))) for i in range(0, 35, 10)],
            ),  # happy_path_uneven_division
            ([], 20, []),  # edge_case_empty_list
            (
                list(range(20)),
                20,
                [list(range(20))],
            ),  # edge_case_list_size_equals_batch_size
            (
                list(range(19)),
                20,
                [list(range(19))],
            ),  # edge_case_list_size_less_than_batch_size
            ([1, 2, 3], 1, [[1], [2], [3]]),  # edge_case_batch_size_one
        ],
        ids=[
            "happy_path_even_division",
            "happy_path_uneven_division",
            "edge_case_empty_list",
            "edge_case_list_size_equals_batch_size",
            "edge_case_list_size_less_than_batch_size",
            "edge_case_batch_size_one",
        ],
    )
    def test_segment_list_happy_path(self, item_list, batch_size, expected_segments):
        # Act
        actual_segments = list(BggXmlApi2._segment_list(item_list, batch_size))

        # Assert
        assert actual_segments == expected_segments

    @pytest.mark.parametrize(
        "item_list, batch_size, expected_error",
        [
            (123, 20, TypeError),  # type: ignore[arg-type] # error_invalid_item_list_type
            (list(range(20)), "20", TypeError),  # type: ignore[arg-type] # error_invalid_batch_size_type
            (list(range(20)), 0, ValueError),  # error_zero_batch_size
            (list(range(20)), -20, ValueError),  # error_negative_batch_size
        ],
        ids=[
            "error_invalid_item_list_type",
            "error_invalid_batch_size_type",
            "error_zero_batch_size",
            "error_negative_batch_size",
        ],
    )
    def test_segment_list_error_cases(self, item_list, batch_size, expected_error):
        # Act & Assert
        with pytest.raises(expected_error):
            list(BggXmlApi2._segment_list(item_list, batch_size))


class TestQueryThing:
    @pytest.mark.parametrize(
        "thing_id, mock_status_code, mock_content, expected_xml",
        [
            (
                "174430",
                200,
                b"<xml>Gloomhaven</xml>",
                "<xml>Gloomhaven</xml>",
            ),  # happy_path_valid_id
            (
                "1",
                200,
                b"<xml>Root</xml>",
                "<xml>Root</xml>",
            ),  # happy_path_another_valid_id
            ("", 200, b"<xml></xml>", "<xml></xml>"),  # edge_case_empty_id
        ],
        ids=[
            "happy_path_valid_id",
            "happy_path_another_valid_id",
            "edge_case_empty_id",
        ],
    )
    def test_query_thing_happy_path(
        self,
        thing_id,
        mock_status_code,
        mock_content,
        expected_xml,
        mocker: MockerFixture,
    ):
        # Arrange
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = mock_status_code
        mock_response.content = mock_content

        mocker.patch("services.pipeline.bggxmlapi2.get", return_value=mock_response)

        # Act
        actual_xml = BggXmlApi2.query_thing(thing_id)

        # Assert
        assert actual_xml == expected_xml

    @pytest.mark.parametrize(
        "thing_id, mock_status_code, expected_exception",
        [
            ("174430", 404, Exception),  # error_404
            ("174430", 500, Exception),  # error_500
        ],
        ids=["error_404", "error_500"],
    )
    def test_query_thing_error_cases(
        self, thing_id, mock_status_code, expected_exception, mocker: MockerFixture
    ):
        # Arrange
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = mock_status_code
        mock_response.content = b""

        mocker.patch("services.pipeline.bggxmlapi2.get", return_value=mock_response)

        # Act & Assert
        with pytest.raises(expected_exception):
            BggXmlApi2.query_thing(thing_id)


class TestBulkQueryThings:
    @pytest.mark.parametrize(
        "thing_ids, mock_responses, expected_xml_batches",
        [
            (
                ["1", "2", "3"],
                [b"<xml>1,2,3</xml>"],
                ["<xml>1,2,3</xml>"],
            ),  # happy_path_single_batch
            (
                list(map(str, range(1, 21))),  # type: ignore[arg-type]
                [b"<xml>1,2,...,20</xml>"],
                ["<xml>1,2,...,20</xml>"],
            ),  # happy_path_full_batch
            (
                list(map(str, range(1, 22))),  # type: ignore[arg-type]
                [b"<xml>1,2,...,20</xml>", b"<xml>21</xml>"],
                ["<xml>1,2,...,20</xml>", "<xml>21</xml>"],
            ),  # happy_path_multiple_batches
            ([], [], []),  # edge_case_empty_list
        ],
        ids=[
            "happy_path_single_batch",
            "happy_path_full_batch",
            "happy_path_multiple_batches",
            "edge_case_empty_list",
        ],
    )
    def test_bulk_query_things_happy_path(
        self, thing_ids, mock_responses, expected_xml_batches, mocker: MockerFixture
    ):
        # Arrange
        mock_response_iter = iter(mock_responses)

        def mock_query_thing(thing_id: str) -> str:
            return next(mock_response_iter).decode()

        mocker.patch.object(BggXmlApi2, "query_thing", side_effect=mock_query_thing)

        # Act
        actual_xml_batches = list(BggXmlApi2.bulk_query_things(thing_ids))

        # Assert
        assert actual_xml_batches == expected_xml_batches

    @pytest.mark.parametrize(
        "thing_ids, mock_response, expected_exception",
        [
            (["1"], b"", Exception),  # error_query_thing_fails
            (123, b"", TypeError),  # type: ignore[arg-type] # error_invalid_thing_ids
        ],
        ids=["error_query_thing_fails", "error_invalid_thing_ids"],
    )
    def test_bulk_query_things_error_cases(
        self, thing_ids, mock_response, expected_exception, mocker: MockerFixture
    ):
        # Arrange
        mocker.patch.object(
            BggXmlApi2, "query_thing", side_effect=Exception("Mock Exception")
        )

        # Act & Assert
        with pytest.raises(expected_exception):
            list(BggXmlApi2.bulk_query_things(thing_ids))

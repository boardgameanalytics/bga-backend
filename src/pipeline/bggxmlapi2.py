import logging
from collections.abc import Generator

from requests import get


class BggXmlApi2:
    BASE_QUERY_URL = "https://boardgamegeek.com/xmlapi2"

    @classmethod
    def _build_query_url(cls, query_type: str, params: dict[str, str]) -> str:
        """
        Build query url for BGG XML API 2

        :param query_type: type of query: thing, user, search...
        :param params: dict of params using str for both keys and values

        :return str: Query URL for given parameters
        """
        params_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{cls.BASE_QUERY_URL}/{query_type}?{params_string}"

    @staticmethod
    def _segment_list(
        item_list: list, batch_size: int = 20
    ) -> Generator[list, None, None]:
        """
        Segment list of items into batches.

        :param item_list: list of items to segment
        :param batch_size: number of items to segment into each batch

        :return Generator[str]: Yields list of segmented items
        """
        if batch_size < 1:
            raise ValueError("batch_size must be greater than 1")

        total_batches = (len(item_list) + batch_size - 1) // batch_size
        logging.info(f"Total batches: {total_batches}")
        for batch_num in range(total_batches):
            begin = batch_num * batch_size
            end = min(begin + batch_size, len(item_list))
            yield item_list[begin:end]

    @classmethod
    def query_thing(cls, thing_id: str) -> str:
        """
        Fetch thing data from BGG

        :param thing_id: numerical id of game on BGG

        :return str: Game data encoded with XML
        """
        request_url = cls._build_query_url("thing", {"stats": "1", "id": thing_id})
        response = get(url=request_url)

        if response.status_code != 200:
            raise Exception(f"BGGXMLAPI2 returned status code: {response.status_code}")

        return response.content.decode()

    @classmethod
    def bulk_query_things(cls, thing_ids: list[str]) -> Generator[str, None, None]:
        """
        Retrieve things data from BGG in bulk

        :param thing_ids: list of ids of games to get

        :return Generator[str]: Yields batches of items
        """
        for batch in cls._segment_list(thing_ids):
            yield cls.query_thing(thing_id=",".join(batch))

import logging
from typing import NamedTuple, Union

import requests

from ..serializers.baka_serializer import BakaSerializer
from ..utils import BakaApiParser, BakaPageScraper

logger = logging.getLogger(__name__)


class BakaPage(NamedTuple):
    html: Union[str, bytes]
    url: str


class BakaRetriever:
    @staticmethod
    def get(baka_url):
        response = requests.get(baka_url, timeout=30)
        response.raise_for_status()
        return BakaPage(html=response.text, url=response.url)


class BakaApiRetriever:
    @staticmethod
    def get(baka_code):
        response = requests.get(BakaSerializer.api_url(baka_code), timeout=30)
        response.raise_for_status()
        return response.json()


class BakaSourceError(Exception):
    pass


class BakaSourceResult(NamedTuple):
    series_data: dict
    baka_id: str


class BakaApiSource:
    """Fetches series data from the official Mangaupdates API. Only works with alphanumeric codes."""

    def __init__(self, retriever=None):
        self.retriever = retriever or BakaApiRetriever()

    @staticmethod
    def accepts(baka_id):
        return bool(baka_id) and not BakaSerializer.is_numeric(baka_id)

    def fetch(self, baka_id):
        try:
            series_json = self.retriever.get(baka_id)
            series_data = BakaApiParser(series_json, baka_id=baka_id).parse()
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            raise BakaSourceError(f"Mangaupdates API failed for {baka_id}: {error!r}") from error
        return BakaSourceResult(series_data=series_data, baka_id=baka_id)


class BakaScraperSource:
    """Scrapes the Mangaupdates series page. Works with any ID; old numeric IDs are upgraded through the redirect."""

    def __init__(self, retriever=None):
        self.retriever = retriever or BakaRetriever()

    @staticmethod
    def accepts(baka_id):
        return bool(baka_id)

    def fetch(self, baka_id):
        serializer = BakaSerializer()
        page = self.retriever.get(serializer.url_for_id(baka_id))
        upgraded_id = serializer.upgraded_id(baka_id, page.url)
        series_data = BakaPageScraper(page_html=page.html, baka_id=upgraded_id).parse()
        return BakaSourceResult(series_data=series_data, baka_id=upgraded_id)


def default_sources():
    return [BakaApiSource(), BakaScraperSource()]


def fetch_from_sources(baka_id, sources=None):
    """Try each source that accepts the ID, in order, moving on to the next one when a source fails."""
    errors = []
    for source in sources if sources is not None else default_sources():
        if not source.accepts(baka_id):
            continue
        try:
            return source.fetch(baka_id)
        except BakaSourceError as error:
            logger.warning("%s; trying next source", error)
            errors.append(error)
    if errors:
        raise errors[-1]
    raise BakaSourceError(f"No source can fetch Mangaupdates ID {baka_id!r}")

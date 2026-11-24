import re
from urllib.parse import urlparse, parse_qs

import requests

from .external_id_finder import ExternalIDFinder
from ..models import MangaSeries


class BakaIDFinder(ExternalIDFinder):
    def __init__(self, title, link_fetcher=None):
        super().__init__(title)
        self.link_fetcher = link_fetcher or LinkFetcher()

    @classmethod
    def accepts(cls, item):
        return isinstance(item, MangaSeries)

    def get_id(self):
        link = self.link_fetcher.fetch(self.title)
        url = urlparse(link)
        alphanumeric_match = re.match(re.compile(r"/series/(\w+)/?.*"), url.path)
        if not url.hostname == 'www.mangaupdates.com':
            raise BakaUrlException(link)
        if alphanumeric_match:
            return alphanumeric_match.group(1)
        if url.path == '/series.html':
            try:
                return int(parse_qs(url.query)["id"][0])
            except KeyError as error:
                raise BakaUrlException(link) from error
        raise BakaUrlException(link)


class BakaSearchRetriever:
    SEARCH_URL = "https://api.mangaupdates.com/v1/series/search"

    def search(self, series_title):
        response = requests.post(self.SEARCH_URL, json={"search": series_title}, timeout=30)
        response.raise_for_status()
        return response.json()["results"]


class LinkFetcher:
    """Finds a series' Mangaupdates URL with the official API search.

    Prefers a result whose matched title equals the series title, otherwise falls back to the first result.
    """

    def __init__(self, retriever=None):
        self.retriever = retriever or BakaSearchRetriever()

    def fetch(self, series_title):
        results = self.retriever.search(series_title)
        if not results:
            raise BakaSearchException(series_title)
        wanted = normalize_title(series_title)
        best = next((result for result in results if normalize_title(result.get("hit_title")) == wanted), results[0])
        return best["record"]["url"]


def normalize_title(title):
    return " ".join((title or "").casefold().split())


class BakaSearchException(Exception):
    def __init__(self, series_title):
        super().__init__(f'Cannot find Mangaupdates page for series "{series_title}"')


class BakaUrlException(Exception):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def __str__(self):
        return f"Cannot get Baka-ID from URL: {self.url}"

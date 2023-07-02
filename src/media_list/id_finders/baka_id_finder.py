import re
from urllib.parse import urlparse, parse_qs

from googlesearch import search

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


class LinkFetcher:
    @staticmethod
    def fetch(series_title):
        for result in search(f"mangaupdates.com {series_title}", advanced=True):
            return result.url
        raise Exception(f'Cannot find Mangaupdates page for series "{series_title}"')


class BakaUrlException(Exception):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def __str__(self):
        return f"Cannot get Baka-ID from URL: {self.url}"

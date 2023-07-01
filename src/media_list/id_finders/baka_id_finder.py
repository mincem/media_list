from urllib.parse import urlparse, parse_qs

import googlesearch

from . import ExternalIDFinder
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
        if not self.source_is_correct(url):
            raise Exception(f"Cannot get Baka-ID from URL: {link}")
        return int(parse_qs(url.query)["id"][0])

    @staticmethod
    def source_is_correct(url):
        return url.hostname == 'www.mangaupdates.com' and url.path == '/series.html'


class LinkFetcher:
    @staticmethod
    def fetch(series_title):
        for url in googlesearch.search(f"site:mangaupdates.com {series_title}", stop=20):
            return url
        raise Exception(f'Cannot find Mangaupdates page for series "{series_title}"')

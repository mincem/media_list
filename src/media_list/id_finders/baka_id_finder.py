from urllib.parse import urlparse, parse_qs

from googlesearch import search

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
        link = self.fetch_link()
        url = urlparse(link)
        if not self.source_is_correct(url):
            raise Exception(f"Cannot get Baka-ID from URL: {link}")
        return int(parse_qs(url.query)["id"][0])

    def fetch_link(self):
        return self.link_fetcher.get(self.title)

    @staticmethod
    def source_is_correct(url):
        return url.hostname == 'www.mangaupdates.com' and url.path == '/series.html'


class LinkFetcher:
    @staticmethod
    def get(series_title):
        for result in search(f"mangaupdates.com {series_title}", advanced=True):
            return result.url
        raise Exception(f'Cannot find Mangaupdates page for series "{series_title}"')

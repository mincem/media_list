import re
from urllib.parse import urlparse, parse_qs

import googlesearch

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
        alphanumeric_match = re.match(re.compile("/series/(\w+)/?.*"), url.path)
        if not url.hostname == 'www.mangaupdates.com':
            raise BakaUrlException(link)
        elif alphanumeric_match:
            return alphanumeric_match.group(1)
        elif url.path == '/series.html':
            try:
                return int(parse_qs(url.query)["id"][0])
            except KeyError:
                raise BakaUrlException(link)
        else:
            raise BakaUrlException(link)



class LinkFetcher:
    @staticmethod
    def fetch(series_title):
        for url in googlesearch.search(f"site:mangaupdates.com {series_title}", stop=20):
            return url
        raise Exception(f'Cannot find Mangaupdates page for series "{series_title}"')

class BakaUrlException(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f"Cannot get Baka-ID from URL: {self.url}"

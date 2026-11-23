import json
from typing import NamedTuple, Union

import requests

from .external_item_fetcher import ExternalItemFetcher
from ..models import MangaSeries
from ..repositories import BakaSeriesRepository
from ..serializers.baka_serializer import BakaSerializer
from ..utils import BakaPageScraper


class ExternalMangaFetcher(ExternalItemFetcher):
    def __init__(self, item, baka_retriever=None, image_retriever_class=None):
        super().__init__(item, image_retriever_class)
        self.baka_retriever = baka_retriever or BakaRetriever()
        self.web_page = None

    @classmethod
    def accepts(cls, item):
        return isinstance(item, MangaSeries)

    def fetch(self):
        parsed_series_data = self.parsed_series_data()
        baka_series = BakaSeriesRepository().create(**parsed_series_data)
        return baka_series

    def display_parsed_data(self):
        return json.dumps(self.parsed_series_data(), indent=2)

    def parsed_series_data(self):
        page = self.baka_web_page()
        # Lazy upgrade: if an old numeric ID was redirected to a code URL, keep the code.
        # The caller is responsible for saving the item.
        self.item.baka_id = BakaSerializer().upgraded_id(self.item.baka_id, page.url)
        series_data = BakaPageScraper(page_html=page.html, baka_id=self.item.baka_id).parse()
        image_url = series_data.pop("image_url")
        if image_url is not None:
            series_data["image"] = self.image_retriever_class(image_url).fetch()
        return series_data

    def baka_web_page(self):
        if self.web_page is None:
            self.web_page = self.baka_retriever.get(BakaSerializer().url(self.item))
        return self.web_page


class BakaPage(NamedTuple):
    html: Union[str, bytes]
    url: str


class BakaRetriever:
    @staticmethod
    def get(baka_url):
        response = requests.get(baka_url)
        response.raise_for_status()
        return BakaPage(html=response.text, url=response.url)

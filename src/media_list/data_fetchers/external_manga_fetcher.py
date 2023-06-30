import json

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
        self.web_page_html = None

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
        series_data = BakaPageScraper(self.baka_web_page_html(), self.item.baka_id).parse()
        image_url = series_data.pop("image_url")
        if image_url is not None:
            series_data["image"] = self.image_retriever_class(image_url).fetch()
        return series_data

    def baka_web_page_html(self):
        if self.web_page_html is None:
            self.web_page_html = self.baka_retriever.get(self.item.baka_id)
        return self.web_page_html


class BakaRetriever:
    @staticmethod
    def get(baka_id):
        response = requests.get(BakaSerializer.numeric_id_url(baka_id))
        response.raise_for_status()
        return response.text

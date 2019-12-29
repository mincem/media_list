import json
import os

import requests
from django.core.files.base import ContentFile

from .baka_page_scraper import BakaPageScraper
from ..repositories import BakaSeriesRepository


class BakaParser:
    def __init__(self, baka_id, baka_retriever=None, image_retriever=None):
        self.baka_id = baka_id
        self.baka_retriever = baka_retriever or BakaRetriever()
        self.image_retriever = image_retriever or BakaImageRetriever()
        self.web_page_html = None

    def perform(self):
        parsed_series_data = self.parsed_series_data()
        baka_series = BakaSeriesRepository().create(**parsed_series_data)
        return baka_series

    def display_parsed_data(self):
        return json.dumps(self.parsed_series_data(), indent=2)

    def parsed_series_data(self):
        return BakaPageScraper(self.baka_web_page_html(), self.baka_id, self.image_retriever).parse()

    def baka_web_page_html(self):
        if self.web_page_html is None:
            self.web_page_html = self.baka_retriever.get(self.baka_id)
        return self.web_page_html


class BakaRetriever:
    @staticmethod
    def get(baka_id):
        response = requests.get(f"https://www.mangaupdates.com/series.html?id={baka_id}")
        response.raise_for_status()
        return response.text


class BakaImageRetriever:
    @staticmethod
    def get(baka_image_url):
        response = requests.get(baka_image_url)
        response.raise_for_status()
        return {
            "name": os.path.basename(baka_image_url),
            "content": ContentFile(response.content),
        }

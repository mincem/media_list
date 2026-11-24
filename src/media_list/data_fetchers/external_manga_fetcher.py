import json

from .baka_sources import fetch_from_sources
from .external_item_fetcher import ExternalItemFetcher
from ..models import MangaSeries
from ..repositories import BakaSeriesRepository


class ExternalMangaFetcher(ExternalItemFetcher):
    def __init__(self, item, sources=None, image_retriever_class=None):
        super().__init__(item, image_retriever_class)
        self.sources = sources
        self.source_result = None

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
        result = self.fetch_series()
        # Lazy upgrade: if an old numeric ID was redirected to a code URL, keep the code.
        # The caller is responsible for saving the item.
        self.item.baka_id = result.baka_id
        series_data = dict(result.series_data)
        image_url = series_data.pop("image_url")
        if image_url is not None:
            series_data["image"] = self.image_retriever_class(image_url).fetch()
        return series_data

    def fetch_series(self):
        if self.source_result is None:
            self.source_result = fetch_from_sources(self.item.baka_id, self.sources)
        return self.source_result

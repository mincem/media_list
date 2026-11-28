import json

from .baka_id_resolver import BakaIDResolver
from .baka_sources import fetch_from_sources
from .external_item_fetcher import ExternalItemFetcher
from ..models import MangaSeries
from ..repositories import BakaSeriesRepository
from ..serializers.baka_serializer import BakaSerializer


class ExternalMangaFetcher(ExternalItemFetcher):
    repository_class = BakaSeriesRepository

    def __init__(self, item, sources=None, image_retriever_class=None, id_resolver=None):
        super().__init__(item, image_retriever_class)
        self.sources = sources
        self.id_resolver = id_resolver or BakaIDResolver()
        self.source_result = None

    @classmethod
    def accepts(cls, item):
        return isinstance(item, MangaSeries)

    def display_parsed_data(self):
        return json.dumps(self.fetch_data(), indent=2, default=str)

    def fetch_data(self):
        """Upgrades an old numeric ID to its code first, so the data always comes from the code (and the API)."""
        if BakaSerializer.is_numeric(self.item.baka_id):
            self.item.baka_id = self.id_resolver.resolve(self.item)
        result = self.fetch_series()
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

from urllib.parse import urlparse

from django.db import models
from ordered_model.models import OrderedModel


class ItemURL(OrderedModel):
    class Meta(OrderedModel.Meta):
        abstract = True

    url = models.URLField()

    def __str__(self):
        return self.url

    def hostname(self):
        return urlparse(self.url).hostname


class MangaURL(ItemURL):
    series = models.ForeignKey("MangaSeries", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'series'


class MovieURL(ItemURL):
    movie = models.ForeignKey("Movie", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'movie'

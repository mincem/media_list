from django.db import models

from . import base_models


class VideoSource(base_models.MediaSource):
    pass


class VideoGenre(base_models.NamedModel):
    pass


class VideoKeyword(base_models.NamedModel):
    pass


class VideoPerson(base_models.NamedModel, base_models.TimestampedModel):
    imdb_id = models.PositiveSmallIntegerField()


class VideoCountry(base_models.NamedModel):
    pass

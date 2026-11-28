from django.db import models

from . import base_models


class VideoSource(base_models.MediaSource):
    pass


class VideoGenre(base_models.NamedModel):
    pass


class VideoKeyword(base_models.NamedModel):
    pass


class VideoPerson(base_models.Person):
    external_id_field = "tmdb_id"

    imdb_id = models.PositiveIntegerField(blank=True, null=True)
    tmdb_id = models.PositiveIntegerField(blank=True, null=True, unique=True)


class VideoCountry(base_models.NamedModel):
    pass

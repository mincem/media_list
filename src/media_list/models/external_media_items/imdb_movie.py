from django.db import models

from . import ExternalMediaItem


class IMDBMovie(ExternalMediaItem):
    imdb_id = models.PositiveSmallIntegerField()
    original_title = models.CharField(max_length=255)
    runtime = models.DurationField(blank=True, null=True)
    countries = models.ManyToManyField("VideoCountry", related_name="movies")
    genres = models.ManyToManyField("VideoGenre", related_name="movies")
    keywords = models.ManyToManyField("VideoKeyword", related_name="movies")
    cast = models.ManyToManyField("VideoPerson", related_name="movies_as_cast", through="MovieCastMember")
    directors = models.ManyToManyField("VideoPerson", related_name="movies_as_director")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    image = models.ImageField(upload_to="movie_images/", blank=True, null=True)

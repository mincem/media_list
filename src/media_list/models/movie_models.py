from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from ordered_model.models import OrderedModel

from .base_models import MediaItem, ItemURL, ExternalMediaItem
from ..categories import movie_category

STATUS_CHOICES = (
    ('U', 'Unknown Status'),
    ('N', 'Not Downloaded'),
    ('D', 'Downloaded'),
    ('S', 'Streaming'),
)
DEFAULT_STATUS_CHOICE = STATUS_CHOICES[0][0]


class Movie(MediaItem):
    category = movie_category

    is_watched = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)
    source = models.ForeignKey("VideoSource", blank=True, null=True, on_delete=models.SET_NULL)
    imdb_id = models.PositiveSmallIntegerField(blank=True, null=True)
    imdb_info = models.ForeignKey("IMDBMovie", blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def external_info(self):
        return self.imdb_info

    @property
    def image_url(self):
        return static('media_list/images/default_cover_2.jpg')

    def external_url(self):
        if not self.imdb_id:
            raise Exception("IMDb URL has not been retrieved yet.")
        return f"https://www.imdb.com/title/tt{str(self.imdb_id).zfill(7)}/"


class MovieURL(ItemURL):
    movie = models.ForeignKey("Movie", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'movie'


class IMDBMovie(ExternalMediaItem):
    imdb_id = models.PositiveSmallIntegerField()
    runtime = models.DurationField(blank=True, null=True)
    countries = models.ManyToManyField("VideoCountry", related_name="movies")
    genres = models.ManyToManyField("VideoGenre", related_name="movies")
    keywords = models.ManyToManyField("VideoKeyword", related_name="movies")
    cast = models.ManyToManyField("VideoPerson", related_name="movies_as_cast", through="MovieCastMember")
    directors = models.ManyToManyField("VideoPerson", related_name="movies_as_director")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    image = models.ImageField(upload_to="movie_images/", blank=True, null=True)


class MoviePlot(OrderedModel):
    movie = models.ForeignKey("IMDBMovie", related_name="plots", on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    order_with_respect_to = 'movie'

    def __str__(self):
        return str(self.text)


class MovieCastMember(OrderedModel):
    movie = models.ForeignKey("IMDBMovie", related_name="ordered_cast", on_delete=models.CASCADE)
    member = models.ForeignKey("VideoPerson", on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    order_with_respect_to = 'movie'

    def __str__(self):
        return str(self.member)

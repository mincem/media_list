from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models

from .base_models import MediaItem, ItemURL
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
    # imdb_info = models.ForeignKey("ImdbMovie", blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def image_url(self):
        return static('media_list/images/default_cover_2.jpg')


class MovieURL(ItemURL):
    movie = models.ForeignKey("Movie", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'movie'

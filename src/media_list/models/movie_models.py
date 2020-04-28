from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from ordered_model.models import OrderedModel

from .video_models import VideoSource
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
    source_class = VideoSource

    is_watched = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)
    source = models.ForeignKey("VideoSource", blank=True, null=True, on_delete=models.SET_NULL)
    imdb_id = models.PositiveSmallIntegerField(blank=True, null=True)
    imdb_info = models.ForeignKey("IMDBMovie", blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def external_id(self):
        return self.imdb_id

    @external_id.setter
    def external_id(self, value):
        self.imdb_id = value

    @property
    def external_info(self):
        return self.imdb_info

    @external_info.setter
    def external_info(self, value):
        self.imdb_info = value

    @property
    def image_url(self):
        if self.external_info and self.external_info.image:
            return self.external_info.image.url
        else:
            return static('media_list/images/default_cover_2.jpg')

    def external_url(self):
        if not self.imdb_id:
            raise Exception("IMDb URL has not been retrieved yet.")
        return f"https://www.imdb.com/title/tt{str(self.imdb_id).zfill(7)}/"


class MovieURL(ItemURL):
    movie = models.ForeignKey("Movie", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'movie'


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

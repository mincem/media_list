from django.db import models
from django.templatetags.static import static

from .base_models import TimestampedModel, NamedModel, MediaItem, MediaSource
from ..categories import manga_category
from ..serializers.baka_serializer import BakaSerializer

STATUS_CHOICES = (
    ('U', 'Unknown Status'),
    ('N', 'Not Downloaded'),
    ('D', 'Downloading'),
    ('R', 'Downloaded Raw'),
    ('E', 'Edited Complete'),
    ('I', 'Edited Incomplete'),
)
DEFAULT_STATUS_CHOICE = STATUS_CHOICES[0][0]


class MangaSource(MediaSource):
    pass


class MangaSeries(MediaItem):
    category = manga_category
    source_class = MangaSource

    volumes = models.IntegerField(blank=True, null=True)
    has_omnibus = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    source = models.ForeignKey("MangaSource", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)
    baka_id = models.PositiveSmallIntegerField(blank=True, null=True)
    baka_code = models.CharField(max_length=63, blank=True, null=True)
    baka_info = models.ForeignKey("BakaSeries", blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def external_id(self):
        return self.baka_code or self.baka_id

    @external_id.setter
    def external_id(self, value):
        if isinstance(value, int) or value.isnumeric():
            self.baka_id = value
        else:
            self.baka_code = value

    @property
    def external_info(self):
        return self.baka_info

    @external_info.setter
    def external_info(self, value):
        self.baka_info = value

    def display_volumes(self):
        if self.volumes == 1 and self.is_completed:
            return 'Omnibus One-shot' if self.has_omnibus else 'One-shot'
        return f"{self.volumes}{'+' if not self.is_completed else ''} {'omnibus' if self.has_omnibus else 'volumes'}"

    def baka_url(self):
        return BakaSerializer().url(self)

    def incomplete(self):
        return self.volumes is None or not self.urls.count() or self.status == DEFAULT_STATUS_CHOICE

    @property
    def image_url(self):
        if self.external_info and self.external_info.image:
            return self.external_info.image.url
        return static('media_list/images/default_cover_2.jpg')


class MangaGenre(NamedModel):
    pass


class MangaKeyword(NamedModel):
    pass


class MangaSeriesKeyword(models.Model):
    class Meta:
        ordering = ['-score']

    baka_series = models.ForeignKey("BakaSeries", related_name="weighed_keywords", on_delete=models.CASCADE)
    keyword = models.ForeignKey("MangaKeyword", on_delete=models.CASCADE)
    score = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.keyword)


class MangaPerson(NamedModel, TimestampedModel):
    pass

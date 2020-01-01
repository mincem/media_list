from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models

from .base import TimestampedModel, NamedModel, MediaItem, ItemURL

STATUS_CHOICES = (
    ('U', 'Unknown Status'),
    ('N', 'Not Downloaded'),
    ('D', 'Downloading'),
    ('R', 'Downloaded Raw'),
    ('E', 'Edited Complete'),
    ('I', 'Edited Incomplete'),
)
DEFAULT_STATUS_CHOICE = STATUS_CHOICES[0][0]


class MangaSeries(MediaItem):
    volumes = models.IntegerField(blank=True, null=True)
    has_omnibus = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    source = models.ForeignKey("MangaSource", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)
    baka_id = models.PositiveSmallIntegerField(blank=True, null=True)
    baka_info = models.ForeignKey("BakaSeries", blank=True, null=True, on_delete=models.SET_NULL)

    def display_volumes(self):
        if self.volumes == 1 and self.is_completed:
            return 'Omnibus One-shot' if self.has_omnibus else 'One-shot'
        return f"{self.volumes}{'+' if not self.is_completed else ''} {'omnibus' if self.has_omnibus else 'volumes'}"

    def baka_url(self):
        if not self.baka_id:
            raise Exception("Mangaupdates URL has not been retrieved yet.")
        return f"https://www.mangaupdates.com/series.html?id={self.baka_id}"

    def incomplete(self):
        return self.volumes is None or not self.urls.count() or self.status == DEFAULT_STATUS_CHOICE

    def swap_titles(self):
        self.title, self.alternate_title = self.alternate_title, self.title
        self.save()

    @property
    def image_url(self):
        if self.baka_info and self.baka_info.image:
            return self.baka_info.image.url
        else:
            return static('media_list/images/default_cover_2.jpg')


class BakaSeries(TimestampedModel):
    baka_id = models.PositiveSmallIntegerField()  # TODO: unique, or save history?
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField("MangaGenre", related_name="series")
    keywords = models.ManyToManyField("MangaKeyword", related_name="series", through="MangaSeriesKeyword")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=255, blank=True)
    authors = models.ManyToManyField("MangaPerson", related_name="series_as_author")
    artists = models.ManyToManyField("MangaPerson", related_name="series_as_artist")
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    original_publisher = models.CharField(max_length=255, blank=True)
    english_publisher = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="manga_images/", blank=True, null=True)

    def __str__(self):
        return f"({self.baka_id}) {self.title}"

    def url(self):
        return f"https://www.mangaupdates.com/series.html?id={self.baka_id}"

    def simple_genre_list(self):
        return ", ".join(str(genre) for genre in self.genres.all())

    def single_author(self):
        if self.has_single_author():
            return self.authors.first()

    def has_single_author(self):
        return self.authors.count() == 1 and self.artists.count() == 1 and self.authors.first() == self.artists.first()

    def staff(self):
        if self.has_single_author():
            return [self.authors.first()]
        return [self.authors.first(), self.artists.first()]

    def has_extra_staff(self):
        return self.authors.count() + self.artists.count() > 2


class MangaSource(NamedModel, TimestampedModel):
    icon = models.ImageField(upload_to="source_icons/", blank=True, null=True)


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


class MangaURL(ItemURL):
    series = models.ForeignKey("MangaSeries", related_name="urls", on_delete=models.CASCADE)
    order_with_respect_to = 'series'
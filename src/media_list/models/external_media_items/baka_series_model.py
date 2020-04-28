from django.db import models

from . import ExternalMediaItem


class BakaSeries(ExternalMediaItem):
    baka_id = models.PositiveSmallIntegerField()
    genres = models.ManyToManyField("MangaGenre", related_name="series")
    keywords = models.ManyToManyField("MangaKeyword", related_name="series", through="MangaSeriesKeyword")
    status = models.CharField(max_length=255, blank=True)
    authors = models.ManyToManyField("MangaPerson", related_name="series_as_author")
    artists = models.ManyToManyField("MangaPerson", related_name="series_as_artist")
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

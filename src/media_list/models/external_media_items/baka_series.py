from django.db import models
from django.db.models import Q

from . import ExternalMediaItem
from ...serializers.baka_serializer import BakaSerializer


class BakaSeries(ExternalMediaItem):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(baka_id__isnull=False) | Q(baka_code__isnull=False),
                name='id_and_code_not_both_null',
                violation_error_message="Fields baka_id and baka_code cannot be both null."
            )
        ]

    baka_id = models.PositiveSmallIntegerField(blank=True, null=True)
    baka_code = models.CharField(max_length=63, blank=True, null=True)
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
        return BakaSerializer.numeric_id_url(self.baka_id)

    def simple_genre_list(self):
        return ", ".join(str(genre) for genre in self.genres.all())

    def single_author(self):
        if self.has_single_author():
            return self.authors.first()
        return None

    def has_single_author(self):
        return self.authors.count() == 1 and self.artists.count() == 1 and self.authors.first() == self.artists.first()

    def staff(self):
        if self.has_single_author():
            return [self.authors.first()]
        return [self.authors.first(), self.artists.first()]

    def has_extra_staff(self):
        return self.authors.count() + self.artists.count() > 2

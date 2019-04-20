from django.db import models

STATUS_CHOICES = (
    ('U', 'Unknown'),
    ('N', 'Not Downloaded'),
    ('D', 'Downloading'),
    ('R', 'Downloaded Raw'),
    ('E', 'Edited'),
)


class MediaSeries(models.Model):
    class Meta:
        ordering = ('title',)

    title = models.CharField(max_length=255)
    alternate_title = models.CharField(blank=True, max_length=255)
    volumes = models.IntegerField(blank=True, null=True)
    has_omnibus = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    source = models.ForeignKey("MangaSource", blank=True, null=True, on_delete=models.SET_NULL)
    url = models.URLField(blank=True, null=True)
    interest = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    notes = models.TextField(blank=True)
    baka_id = models.PositiveSmallIntegerField(blank=True, null=True)
    baka_info = models.ForeignKey("BakaSeries", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def display_volumes(self):
        return f"{self.volumes}{'+' if not self.is_completed else ''} {'omnibus' if self.has_omnibus else 'volumes'}"


class BakaSeries(models.Model):
    baka_id = models.PositiveSmallIntegerField()  # TODO: unique, or save history?
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField("MangaGenre", related_name="series")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey("MangaPerson", related_name="series_as_author", blank=True, null=True,
                               on_delete=models.SET_NULL)
    artist = models.ForeignKey("MangaPerson", related_name="series_as_artist", blank=True, null=True,
                               on_delete=models.SET_NULL)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    original_publisher = models.CharField(max_length=255, blank=True)
    english_publisher = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="manga_images/", blank=True, null=True)


class NamedModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('name',)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class MangaSource(NamedModel):
    icon = models.ImageField(upload_to="source_icons/", blank=True, null=True)


class MangaGenre(NamedModel):
    pass


class MangaPerson(NamedModel):
    pass

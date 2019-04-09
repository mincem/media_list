from django.db import models

STATUS_CHOICES = (
    ('N', 'Not Downloaded'),
    ('D', 'Downloading'),
    ('R', 'Downloaded Raw'),
    ('E', 'Edited'),
)


class MediaSeries(models.Model):
    class Meta:
        ordering = ['title', ]

    title = models.CharField(max_length=255)
    alternate_title = models.CharField(blank=True, max_length=255)
    volumes = models.IntegerField(default=0)
    has_omnibus = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    interest = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def display_volumes(self):
        return f"{self.volumes}{'+' if not self.is_completed else ''} {'omnibus' if self.has_omnibus else 'volumes'}"


class BakaSeries(models.Model):
    baka_id = models.PositiveSmallIntegerField()  # TODO: unique, or save history?
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)  # TODO: genres, plural?
    description = models.TextField(blank=True)
    status = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    original_publisher = models.CharField(max_length=255)
    english_publisher = models.CharField(max_length=255)
    # image = models.ImageField()

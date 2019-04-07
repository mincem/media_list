from django.db import models

STATUS_CHOICES = (
    ('N', 'Not Downloaded'),
    ('D', 'Downloading'),
    ('R', 'Downloaded Raw'),
    ('E', 'Edited'),
)


class MediaSeries(models.Model):
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

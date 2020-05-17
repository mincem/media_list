from django.db import models

from ..base_models import TimestampedModel


class ExternalMediaItem(TimestampedModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)

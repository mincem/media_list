from django.db import models


class TimestampedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NamedModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('name',)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class MediaItem(TimestampedModel):
    class Meta:
        abstract = True
        ordering = ('title',)

    title = models.CharField(max_length=255)
    interest = models.IntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def interest_color(self):
        from ..utils import ColorPicker
        return ColorPicker().color_for(self.interest)

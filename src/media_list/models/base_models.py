from django.db import models
from urllib.parse import urlparse
from ordered_model.models import OrderedModel


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

    category = None

    title = models.CharField(max_length=255)
    alternate_title = models.CharField(blank=True, max_length=255)
    interest = models.IntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    @property
    def interest_color(self):
        from ..utils import ColorPicker
        return ColorPicker().color_for(self.interest)

    @property
    def get_category(self):
        if not type(self).category:
            return f"Undefined category for model {type(self)}"
        return type(self).category


class ItemURL(OrderedModel):
    class Meta:
        abstract = True

    url = models.URLField()

    def __str__(self):
        return self.url

    def hostname(self):
        return urlparse(self.url).hostname


class VideoSource(NamedModel, TimestampedModel):
    icon = models.ImageField(upload_to="source_icons/", blank=True, null=True)

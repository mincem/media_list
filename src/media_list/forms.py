from django.forms import ModelForm
from .models import MangaSeries


class MangaSeriesCreateForm(ModelForm):
    class Meta:
        model = MangaSeries
        fields = [
            "title",
            "alternate_title",
            "volumes",
            "has_omnibus",
            "is_completed",
            "is_read",
            "source",
            "interest",
            "status",
            "notes",
            "baka_id",
        ]

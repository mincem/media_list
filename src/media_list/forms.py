from django.forms import ModelForm
from .models import MangaSeries
from .widgets import RangeInput


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
        widgets = {
            'interest': RangeInput(attrs={'min': 0, 'max': 100})
        }

from django.forms import ModelForm, Textarea
from extra_views import InlineFormSetFactory

from .models import MangaSeries, MangaURL
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
            'interest': RangeInput(attrs={'min': 0, 'max': 100}),
            'notes': Textarea(attrs={'rows': 3}),
        }


class MangaURLInline(InlineFormSetFactory):
    model = MangaURL
    fields = ['url']

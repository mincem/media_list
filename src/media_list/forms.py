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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

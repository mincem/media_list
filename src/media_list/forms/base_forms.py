from django.forms import ModelForm, Textarea

from src.media_list.widgets import RangeInput


class MediaItemForm(ModelForm):
    class Meta:
        widgets = {
            'interest': RangeInput(attrs={'min': 0, 'max': 100}),
            'notes': Textarea(attrs={'rows': 3}),
        }

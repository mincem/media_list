from extra_views import InlineFormSetFactory

from .base_forms import MediaItemForm
from ..models import MangaSeries, MangaURL


class MangaForm(MediaItemForm):
    class Meta(MediaItemForm.Meta):
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
            "baka_code",
        ]


class MangaURLInline(InlineFormSetFactory):
    model = MangaURL
    fields = ['url']

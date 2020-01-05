from extra_views import InlineFormSetFactory

from .base_forms import MediaItemForm
from ..models import Movie, MovieURL


class MovieForm(MediaItemForm):
    class Meta(MediaItemForm.Meta):
        model = Movie
        fields = [
            "title",
            "alternate_title",
            "is_watched",
            "interest",
            "status",
            "notes",
            "imdb_id",
        ]


class MovieURLInline(InlineFormSetFactory):
    model = MovieURL
    fields = ['url']

from . import base_views as media_views
from ..forms import MovieForm, MovieURLInline
from ..models import Movie


class MovieMixin:
    model = Movie


class MovieFormMixin(MovieMixin):
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieListView(MovieMixin, media_views.ListView):
    pass


class MovieGridView(MovieMixin, media_views.GridView):
    pass


class MovieDetailView(MovieMixin, media_views.DetailView):
    pass


class MovieFetchExternalIDView(MovieMixin, media_views.FetchExternalIDView):
    pass


class MovieFetchExternalItemView(MovieMixin, media_views.FetchExternalItemView):
    pass


class MovieSwapTitlesView(MovieMixin, media_views.SwapTitlesView):
    pass


class MovieCreateView(MovieFormMixin, media_views.CreateView):
    pass


class MovieEditView(MovieFormMixin, media_views.EditView):
    pass


class MovieEditInterestView(MovieMixin, media_views.EditInterestView):
    pass


class MovieEditTitleView(MovieMixin, media_views.EditTitleView):
    pass


class MovieEditAlternateTitleView(MovieMixin, media_views.EditAlternateTitleView):
    pass


class MovieDeleteView(MovieMixin, media_views.DeleteView):
    pass

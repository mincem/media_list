from django.views import generic

from . import base_views as media_views
from ..data_fetchers import MovieDataFetcher
from ..forms import MovieForm, MovieURLInline
from ..id_finders import MovieIDFinder
from ..models import Movie, VideoSource


class MovieMixin:
    model = Movie


class MovieDetailMixin(MovieMixin):
    template_name = 'media_list/categories/movie/detail.html'


class MovieFormMixin(MovieMixin):
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieListView(MovieMixin, media_views.ListView):
    source_class = VideoSource


class MovieGridView(MovieMixin, media_views.GridView):
    source_class = VideoSource


class MovieDetailView(MovieDetailMixin, generic.DetailView):
    pass


class MovieFetchExternalIDView(MovieDetailMixin, media_views.FetchExternalIDView):
    def fetch_id(self):
        return MovieIDFinder(self.get_object().title).get_id()


class MovieFetchExternalItemView(MovieDetailMixin, media_views.FetchExternalItemView):
    def fetch_external_info(self):
        return MovieDataFetcher(movie=self.get_object()).get_data()


class MovieSwapTitlesView(MovieDetailMixin, media_views.SwapTitlesView):
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

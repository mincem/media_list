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


class MovieFetchExternalIDView(MovieDetailMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.imdb_id = MovieIDFinder(item.title).get_id()
        item.save()
        return super().get(self, request, *args, **kwargs)


class MovieFetchExternalItemView(MovieDetailMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.imdb_info = MovieDataFetcher(movie=item).get_data()
        item.save()
        return super().get(self, request, *args, **kwargs)


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

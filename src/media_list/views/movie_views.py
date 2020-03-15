from django.views import generic

from . import base_views as media_views
from ..data_fetchers import MovieDataFetcher
from ..forms import MovieForm, MovieURLInline
from ..id_finders import MovieIDFinder
from ..models import Movie, VideoSource


class MovieCollectionView(generic.ListView):
    model = Movie

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            sources=VideoSource.objects.all(),
            series_id=self.kwargs.get('pk'),
            **kwargs
        )


class MovieListView(MovieCollectionView):
    template_name = 'media_list/categories/movie/list.html'


class MovieGridView(MovieCollectionView):
    template_name = 'media_list/categories/movie/grid.html'


class MovieDetailMixin:
    model = Movie
    template_name = 'media_list/categories/movie/detail.html'


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


class MovieSwapTitlesView(MovieDetailMixin, media_views.MediaSwapTitlesView):
    pass


class MovieCreateView(media_views.MediaCreateView):
    model = Movie
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieEditView(media_views.MediaEditView):
    model = Movie
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieEditInterestView(media_views.EditInterestView):
    model = Movie


class MovieDeleteView(media_views.MediaDeleteView):
    model = Movie

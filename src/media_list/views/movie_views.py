from django.views import generic

from .base_views import EditInterestView, MediaCreateView, MediaEditView, MediaDeleteView
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


class MovieDetailView(generic.DetailView):
    model = Movie
    template_name = 'media_list/categories/movie/detail.html'


class MovieFetchExternalIDView(MovieDetailView):
    def get(self, request, *args, **kwargs):
        movie = self.get_object()
        movie.imdb_id = MovieIDFinder(movie.title).get_id()
        movie.save()
        return super().get(self, request, *args, **kwargs)


class MovieFetchExternalItemView(MovieDetailView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.imdb_info = MovieDataFetcher(movie=object).get_data()
        object.save()
        return super().get(self, request, *args, **kwargs)


class MovieSwapTitlesView(MovieDetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)


class MovieCreateView(MediaCreateView):
    model = Movie
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieEditView(MediaEditView):
    model = Movie
    form_class = MovieForm
    inlines = [MovieURLInline]


class MovieEditInterestView(EditInterestView):
    model = Movie


class MovieDeleteView(MediaDeleteView):
    model = Movie

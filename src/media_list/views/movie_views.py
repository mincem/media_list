from django.views import generic

from .base_views import EditInterestView, MediaCreateView, MediaEditView, MediaDeleteView
from ..forms import MovieForm, MovieURLInline
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

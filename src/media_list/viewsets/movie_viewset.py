from .viewset import Viewset
from ..views import movie_views

movie_viewset = Viewset(
    list_view=movie_views.MovieListView,
    grid_view=movie_views.MovieGridView,
    detail_view=movie_views.MovieDetailView,
    create_view=movie_views.MovieCreateView,
    edit_view=movie_views.MovieEditView,
    edit_interest_view=movie_views.MovieEditInterestView,
    delete_view=movie_views.MovieDeleteView,
    find_external_id_view=movie_views.MovieFetchExternalIDView,
    swap_titles_view=movie_views.MovieSwapTitlesView,
)

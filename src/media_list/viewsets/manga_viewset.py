from .viewset import Viewset
from ..views import manga_views

manga_viewset = Viewset(
    list_view=manga_views.MangaListView,
    grid_view=manga_views.MangaGridView,
    detail_view=manga_views.MangaDetailView,
    create_view=manga_views.MangaCreateView,
    edit_view=manga_views.MangaEditView,
    edit_interest_view=manga_views.MangaEditInterestView,
    edit_title_view=manga_views.MangaEditTitleView,
    edit_alternate_title_view=manga_views.MangaEditAlternateTitleView,
    delete_view=manga_views.MangaDeleteView,
    find_external_id_view=manga_views.MangaFetchBakaIDView,
    find_external_data_view=manga_views.MangaFetchBakaInfoView,
    swap_titles_view=manga_views.MangaSwapTitlesView,
)

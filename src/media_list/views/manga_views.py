from django.views import generic

from . import base_views as media_views
from ..forms import MangaForm, MangaURLInline
from ..id_finders import BakaIDFinder
from ..models import MangaSeries, MangaSource
from ..utils import BakaParser


class MangaMixin:
    model = MangaSeries


class MangaDetailMixin(MangaMixin):
    template_name = 'media_list/categories/manga/detail.html'


class MangaFormMixin(MangaMixin):
    form_class = MangaForm
    inlines = [MangaURLInline]


class MangaListView(MangaMixin, media_views.ListView):
    source_class = MangaSource


class MangaGridView(MangaMixin, media_views.GridView):
    source_class = MangaSource


class MangaDetailView(MangaDetailMixin, generic.DetailView):
    pass


class MangaFetchExternalIDView(MangaDetailMixin, media_views.FetchExternalIDView):
    id_finder_class = BakaIDFinder


class MangaFetchExternalItemView(MangaDetailMixin, media_views.FetchExternalItemView):
    def fetch_external_info(self):
        return BakaParser(self.get_object().external_id).perform()


class MangaSwapTitlesView(MangaDetailMixin, media_views.SwapTitlesView):
    pass


class MangaCreateView(MangaFormMixin, media_views.CreateView):
    pass


class MangaEditView(MangaFormMixin, media_views.EditView):
    pass


class MangaEditInterestView(MangaMixin, media_views.EditInterestView):
    pass


class MangaEditTitleView(MangaMixin, media_views.EditTitleView):
    pass


class MangaEditAlternateTitleView(MangaMixin, media_views.EditAlternateTitleView):
    pass


class MangaDeleteView(MangaMixin, media_views.DeleteView):
    pass

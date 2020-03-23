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


class MangaCollectionView(MangaMixin, generic.ListView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            sources=MangaSource.objects.all(),
            series_id=self.kwargs.get('pk'),
            **kwargs
        )


class MangaListView(MangaCollectionView):
    template_name = 'media_list/categories/manga/list.html'


class MangaGridView(MangaCollectionView):
    template_name = 'media_list/categories/manga/grid.html'


class MangaDetailView(MangaDetailMixin, generic.DetailView):
    pass


class MangaFetchBakaIDView(MangaDetailMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_id = BakaIDFinder(series.title).get_id()
        series.save()
        return super().get(self, request, *args, **kwargs)


class MangaFetchBakaInfoView(MangaDetailMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_info = BakaParser(series.baka_id).perform()
        series.save()
        return super().get(self, request, *args, **kwargs)


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

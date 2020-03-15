from django.views import generic

from .base_views import EditInterestView, MediaCreateView, MediaEditView, MediaDeleteView, MediaSwapTitlesView
from ..forms import MangaForm, MangaURLInline
from ..id_finders import BakaIDFinder
from ..models import MangaSeries, MangaSource
from ..utils import BakaParser


class MangaCollectionView(generic.ListView):
    model = MangaSeries

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


class MangaDetailMixin:
    model = MangaSeries
    template_name = 'media_list/categories/manga/detail.html'


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


class MangaSwapTitlesView(MangaDetailMixin, MediaSwapTitlesView):
    pass


class MangaCreateView(MediaCreateView):
    model = MangaSeries
    form_class = MangaForm
    inlines = [MangaURLInline]


class MangaEditView(MediaEditView):
    model = MangaSeries
    form_class = MangaForm
    inlines = [MangaURLInline]


class MangaEditInterestView(EditInterestView):
    model = MangaSeries


class MangaDeleteView(MediaDeleteView):
    model = MangaSeries

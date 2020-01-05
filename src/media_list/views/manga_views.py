from django.views import generic

from .base_views import EditInterestView, MediaCreateView, MediaEditView, MediaDeleteView
from ..forms import MangaForm, MangaURLInline
from ..models import MangaSeries, MangaSource
from ..utils import BakaFinder, BakaParser


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


class MangaDetailView(generic.DetailView):
    model = MangaSeries
    template_name = 'media_list/categories/manga/detail.html'


class MangaFetchBakaIDView(MangaDetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_id = BakaFinder(series.title).baka_id()
        series.save()
        return super().get(self, request, *args, **kwargs)


class MangaFetchBakaInfoView(MangaDetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_info = BakaParser(series.baka_id).perform()
        series.save()
        return super().get(self, request, *args, **kwargs)


class MangaSwapTitlesView(MangaDetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)


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

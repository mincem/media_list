from django.urls import reverse_lazy
from django.views import generic
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from .base_views import EditInterestView
from ..forms import MangaSeriesCreateForm, MangaURLInline
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


class MangaCreateView(CreateWithInlinesView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    inlines = [MangaURLInline]
    template_name = "media_list/categories/manga/forms/manga_series_create_form.html"

    def get_success_url(self):
        if "add_another" in self.request.POST:
            return reverse_lazy('categories:manga:create')
        return reverse_lazy("categories:manga:index_and_modal", kwargs={"pk": self.object.id})


class MangaEditView(UpdateWithInlinesView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    inlines = [MangaURLInline]
    template_name = "media_list/categories/manga/forms/manga_series_edit_form.html"

    def get_success_url(self):
        return reverse_lazy("categories:manga:index_and_modal", kwargs={"pk": self.object.id})


class MangaEditInterestView(EditInterestView):
    model = MangaSeries


class MangaDeleteView(generic.DeleteView):
    model = MangaSeries
    success_url = reverse_lazy("categories:manga:list")

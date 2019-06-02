from django.urls import reverse_lazy
from django.views import generic

from .forms import MangaSeriesCreateForm
from .models import MangaSeries, MangaSource
from .utils import BakaFinder, BakaParser


class IndexView(generic.ListView):
    template_name = 'media_list/index.html'
    context_object_name = 'series_list'
    model = MangaSeries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = MangaSource.objects.all()
        return context


class DetailView(generic.DetailView):
    model = MangaSeries
    template_name = 'media_list/detail.html'


class FetchBakaIDView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_id = BakaFinder(series.title).baka_id()
        series.save()
        return super().get(self, request, *args, **kwargs)


class FetchBakaInfoView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        baka_info = BakaParser(series.baka_id).perform()
        series.baka_info = baka_info
        series.save()
        return super().get(self, request, *args, **kwargs)


class SwapMangaSeriesTitlesView(DetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)


class CreateView(generic.CreateView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    template_name = "media_list/forms/manga_series_create_form.html"
    success_url = reverse_lazy("index")


class EditView(generic.UpdateView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    template_name = "media_list/forms/manga_series_edit_form.html"
    success_url = reverse_lazy("index")


class DeleteView(generic.DeleteView):
    model = MangaSeries
    success_url = reverse_lazy("index")

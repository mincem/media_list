from django.urls import reverse_lazy
from django.views import generic

from .forms import MangaSeriesCreateForm
from .models import MangaSeries
from .utils import BakaFinder, BakaParser


class IndexView(generic.ListView):
    template_name = 'media_list/index.html'
    context_object_name = 'series_list'

    def get_queryset(self):
        return MangaSeries.objects.all()


class DetailView(generic.DetailView):
    model = MangaSeries
    template_name = 'media_list/detail.html'


class FetchBakaIDView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        try:
            series.baka_id = BakaFinder(series.title).baka_id()
            series.save()
        except Exception:
            pass
        return super().get(self, request, *args, **kwargs)


class FetchBakaInfoView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        try:
            baka_info = BakaParser(series.baka_id).perform()
            series.baka_info = baka_info
            series.save()
        except Exception:
            pass
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

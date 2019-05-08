from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import generic

from .forms import MediaSeriesCreateForm
from .models import MediaSeries
from .utils import ScanListParser, BakaFinder, BakaParser


class IndexView(generic.ListView):
    template_name = 'media_list/index.html'
    context_object_name = 'series_list'

    def get_queryset(self):
        return MediaSeries.objects.all()


class DetailView(generic.DetailView):
    model = MediaSeries
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
    model = MediaSeries
    form_class = MediaSeriesCreateForm
    template_name = "media_list/forms/media_series_create_form.html"
    success_url = reverse_lazy("index")


class MagicView(generic.View):
    def get(self, _request, *_args, **_kwargs):
        filename = "./media_list/samples/scans_half.html"
        result = ScanListParser(filename).perform()
        # result = "No magic today"
        return JsonResponse(result.update({"result": "Finished!"}))

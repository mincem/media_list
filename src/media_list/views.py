from django.http import JsonResponse
from django.views import generic

from .models import MediaSeries
from .utils import ScanListParser


class IndexView(generic.ListView):
    template_name = 'media_list/index.html'
    context_object_name = 'series_list'

    def get_queryset(self):
        return MediaSeries.objects.all()


class DetailView(generic.DetailView):
    model = MediaSeries
    template_name = 'media_list/detail.html'


class MagicView(generic.View):
    def get(self, _request, *_args, **_kwargs):
        filename = "./media_list/samples/scans_half.html"
        result = ScanListParser(filename).perform()
        # result = "No magic today"
        return JsonResponse(result.update({"result": "Finished!"}))

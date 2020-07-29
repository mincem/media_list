from django.http import JsonResponse
from django.views import generic

from ..forms import BatchImporterInputForm


class BatchMangaImporterView(generic.FormView):
    template_name = 'media_list/batch_importer/import.html'
    form_class = BatchImporterInputForm

    def form_invalid(self, form):
        return JsonResponse({"error": "error"}, status=400)

    def form_valid(self, form):
        return JsonResponse({
            "items": [data_1(), data_2()]
        })


def data_1():
    return {
        "link": "https://example.com/1",
        "title": "An example",
        "volumes": 20,
        "matches": [{
            "id": 123,
            "title": "An example",
            "volumes": 19,
            "links": [
                {"id": 8, "url": "https://example.com/123"},
                {"id": 9, "url": "https://example.com/456"},
            ],
        }],
    }


def data_2():
    return {
        "link": "https://example.com/2",
        "title": "Another example",
        "volumes": 5,
        "matches": [],
    }

from django.http import JsonResponse
from django.views import generic

from ..forms import BatchImporterInputForm
from ..parsers import link_list_parser


class BatchMangaImporterView(generic.FormView):
    template_name = 'media_list/batch_importer/import.html'
    form_class = BatchImporterInputForm

    def form_invalid(self, form):
        return JsonResponse({"error": "error"}, status=400)

    def form_valid(self, form):
        return JsonResponse({
            "items": link_list_parser.process_markdown(form.cleaned_data['links'])
        })

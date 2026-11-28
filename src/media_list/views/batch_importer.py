import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import ensure_csrf_cookie

from ..parsers import link_list_parser
from ..serializers.batch_importer_serializers import BatchImporterInputSerializer


@method_decorator(ensure_csrf_cookie, name='get')
class BatchMangaImporterView(generic.TemplateView):
    """Shows the importer page, and parses the links it posts as JSON: {"links": [{"text": ..., "url": ...}]}."""
    template_name = 'media_list/batch_importer/import.html'

    def post(self, request, *_args, **_kwargs):
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({"error": "Request body is not valid JSON."}, status=400)
        serializer = BatchImporterInputSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)
        return JsonResponse({
            "items": link_list_parser.process_links(serializer.validated_data["links"])
        })

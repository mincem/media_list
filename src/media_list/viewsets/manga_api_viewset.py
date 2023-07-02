from rest_framework import viewsets

from ..models import MangaSeries
from ..serializers.manga_serializers import MangaSerializer


class MangaApiViewSet(viewsets.ModelViewSet):
    queryset = MangaSeries.objects.all()
    serializer_class = MangaSerializer

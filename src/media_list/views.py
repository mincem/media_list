from django.views import generic

from .models import MediaSeries


class IndexView(generic.ListView):
    template_name = 'media_list/index.html'
    context_object_name = 'series_list'

    def get_queryset(self):
        return MediaSeries.objects.all()


class DetailView(generic.DetailView):
    model = MediaSeries
    template_name = 'media_list/detail.html'

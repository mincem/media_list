from django.urls import reverse_lazy
from django.views import generic
from extra_views import InlineFormSetFactory, CreateWithInlinesView, UpdateWithInlinesView

from ..forms import MangaSeriesCreateForm
from ..models import MangaSeries, MangaSource, MangaURL
from ..utils import BakaFinder, BakaParser


class IndexView(generic.ListView):
    template_name = 'media_list/categories/manga/list.html'
    context_object_name = 'series_list'
    model = MangaSeries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = MangaSource.objects.all()
        context['series_id'] = self.kwargs.get('pk')
        return context


class DetailView(generic.DetailView):
    model = MangaSeries
    template_name = 'media_list/categories/manga/detail.html'


class FetchBakaIDView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_id = BakaFinder(series.title).baka_id()
        series.save()
        return super().get(self, request, *args, **kwargs)


class FetchBakaInfoView(DetailView):
    def get(self, request, *args, **kwargs):
        series = self.get_object()
        series.baka_info = BakaParser(series.baka_id).perform()
        series.save()
        return super().get(self, request, *args, **kwargs)


class SwapMangaSeriesTitlesView(DetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)


class URLInline(InlineFormSetFactory):
    model = MangaURL
    fields = ['url']


class CreateView(CreateWithInlinesView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    inlines = [URLInline]
    template_name = "media_list/categories/manga/forms/manga_series_create_form.html"

    def get_success_url(self):
        if "add_another" in self.request.POST:
            return reverse_lazy('categories:manga:create')
        return reverse_lazy("categories:manga:index_and_modal", kwargs={"pk": self.object.id})


class EditView(UpdateWithInlinesView):
    model = MangaSeries
    form_class = MangaSeriesCreateForm
    inlines = [URLInline]
    template_name = "media_list/categories/manga/forms/manga_series_edit_form.html"

    def get_success_url(self):
        return reverse_lazy("categories:manga:index_and_modal", kwargs={"pk": self.object.id})


class EditInterestView(generic.UpdateView):
    model = MangaSeries
    fields = ['interest']

    def get_success_url(self):
        return reverse_lazy("categories:manga:detail", kwargs={"pk": self.object.id})


class DeleteView(generic.DeleteView):
    model = MangaSeries
    success_url = reverse_lazy("categories:manga:index")

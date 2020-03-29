from django.urls import reverse_lazy
from django.views import generic
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


class LandingView(generic.TemplateView):
    template_name = 'media_list/landing.html'


class CollectionView(generic.ListView):
    def get_sources(self):
        if self.model.source_class:
            return self.model.source_class.objects.all()
        else:
            return []

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            sources=self.get_sources(),
            series_id=self.kwargs.get('pk'),
            **kwargs
        )


class ListView(CollectionView):
    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/list.html"]


class GridView(CollectionView):
    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/grid.html"]


class DetailView(generic.DetailView):
    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/detail.html"]


class FetchExternalIDView(DetailView):
    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.external_id = self.model.id_finder_class(item.title).get_id()
        item.save()
        return super().get(self, request, *args, **kwargs)


class FetchExternalItemView(DetailView):
    def get(self, request, *args, **kwargs):
        item = self.get_object()
        item.external_info = self.fetch_external_info()
        item.save()
        return super().get(self, request, *args, **kwargs)

    def fetch_external_info(self):
        raise NotImplementedError


class CreateView(CreateWithInlinesView):
    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/create.html"]

    def get_success_url(self):
        if "add_another" in self.request.POST:
            return reverse_lazy(f"categories:{self.model.category.path}:create")
        return reverse_lazy(f"categories:{self.model.category.path}:list", kwargs={"pk": self.object.id})


class EditView(UpdateWithInlinesView):
    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/edit.html"]

    def get_success_url(self):
        return reverse_lazy(f"categories:{self.model.category.path}:list", kwargs={"pk": self.object.id})


class EditFieldsView(generic.UpdateView):
    category = None

    def get_success_url(self):
        return reverse_lazy(
            f"categories:{self.get_category().path}:detail",
            kwargs={"pk": self.object.id}
        )

    def get_category(self):
        if self.category:
            return self.category
        if self.model and self.model.category:
            return self.model.category
        raise NotImplementedError


class EditInterestView(EditFieldsView):
    fields = ['interest']


class EditTitleView(EditFieldsView):
    fields = ['title']


class EditAlternateTitleView(EditFieldsView):
    fields = ['alternate_title']


class DeleteView(generic.DeleteView):
    template_name = "media_list/categories/base/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(f"categories:{self.model.category.path}:list")


class SwapTitlesView(DetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)

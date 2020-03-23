from django.urls import reverse_lazy
from django.views import generic
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


class LandingView(generic.TemplateView):
    template_name = 'media_list/landing.html'


class CollectionView(generic.ListView):
    source_class = None

    def get_sources(self):
        if self.source_class:
            return self.source_class.objects.all()
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


class SwapTitlesView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)

from django.urls import reverse_lazy
from django.views import generic
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


class LandingView(generic.TemplateView):
    template_name = 'media_list/landing.html'


class MediaCreateView(CreateWithInlinesView):

    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/create.html"]

    def get_success_url(self):
        if "add_another" in self.request.POST:
            return reverse_lazy(f"categories:{self.model.category.path}:create")
        return reverse_lazy(f"categories:{self.model.category.path}:list", kwargs={"pk": self.object.id})


class MediaEditView(UpdateWithInlinesView):

    def get_template_names(self):
        return [f"media_list/categories/{self.model.category.path}/edit.html"]

    def get_success_url(self):
        return reverse_lazy(f"categories:{self.model.category.path}:list", kwargs={"pk": self.object.id})


class EditInterestView(generic.UpdateView):
    fields = ['interest']
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


class MediaDeleteView(generic.DeleteView):
    template_name = "media_list/categories/base/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(f"categories:{self.model.category.path}:list")


class MediaSwapTitlesView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        self.get_object().swap_titles()
        return super().get(self, request, *args, **kwargs)

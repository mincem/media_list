from django.urls import reverse_lazy
from django.views import generic


class LandingView(generic.TemplateView):
    template_name = 'media_list/landing.html'


class EditInterestView(generic.UpdateView):
    fields = ['interest']
    category = None

    def get_success_url(self):
        return reverse_lazy(
            f"categories:{self.get_category()}:detail",
            kwargs={"pk": self.object.id}
        )

    def get_category(self):
        if self.category:
            return self.category
        raise NotImplementedError

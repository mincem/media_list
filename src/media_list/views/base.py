from django.views import generic


class LandingView(generic.TemplateView):
    template_name = 'media_list/landing.html'

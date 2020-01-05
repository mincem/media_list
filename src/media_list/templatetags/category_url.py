from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def category_url(category, path, *args, **kwargs):
    try:
        category_path = category.path
    except AttributeError:
        return
    return reverse(f"categories:{category_path}:{path}", args=args, kwargs=kwargs)

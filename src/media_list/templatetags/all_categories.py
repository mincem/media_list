from django import template

from .. import categories

register = template.Library()


@register.simple_tag
def all_categories():
    return categories.all_categories()

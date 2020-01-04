from django import template

register = template.Library()


@register.simple_tag
def all_categories():
    return [
        {
            "name": "manga",
            "path": "manga",
        },
        {
            "name": "movies",
            "path": "movies",
        },
    ]

from django.contrib import admin

from .models import MangaSeries, BakaSeries, MangaSource, MangaGenre, MangaPerson

admin.site.register(MangaSeries)
admin.site.register(BakaSeries)
admin.site.register(MangaSource)
admin.site.register(MangaGenre)
admin.site.register(MangaPerson)

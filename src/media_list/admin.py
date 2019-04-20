from django.contrib import admin

from .models import MediaSeries, BakaSeries, MangaSource, MangaGenre, MangaPerson

admin.site.register(MediaSeries)
admin.site.register(BakaSeries)
admin.site.register(MangaSource)
admin.site.register(MangaGenre)
admin.site.register(MangaPerson)

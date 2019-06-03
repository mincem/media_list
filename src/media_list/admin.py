from django.contrib import admin

from .models import MangaSeries, BakaSeries, MangaSource, MangaGenre, MangaPerson, MangaURL


class URLInline(admin.TabularInline):
    model = MangaURL


@admin.register(MangaSeries)
class MangaSeriesAdmin(admin.ModelAdmin):
    inlines = [URLInline]
    search_fields = ['title']


@admin.register(BakaSeries)
class BakaSeriesAdmin(admin.ModelAdmin):
    pass


@admin.register(MangaSource)
class MangaSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(MangaGenre)
class MangaGenreAdmin(admin.ModelAdmin):
    pass


@admin.register(MangaPerson)
class MangaPersonAdmin(admin.ModelAdmin):
    pass


@admin.register(MangaURL)
class MangaURLAdmin(admin.ModelAdmin):
    pass

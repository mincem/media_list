from django.contrib import admin

from .models import MangaSeries, BakaSeries, MangaSource, MangaGenre, MangaPerson, MangaURL, MangaSeriesKeyword, \
    Movie, MovieURL


class MangaURLInline(admin.TabularInline):
    model = MangaURL


@admin.register(MangaSeries)
class MangaSeriesAdmin(admin.ModelAdmin):
    inlines = [MangaURLInline]
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


@admin.register(MangaSeriesKeyword)
class MangaKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'baka_series', 'score']


class MovieURLInline(admin.TabularInline):
    model = MovieURL


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieURLInline]
    search_fields = ['title']

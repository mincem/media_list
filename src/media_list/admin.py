from django.contrib import admin

from . import models


class MangaURLInline(admin.TabularInline):
    model = models.MangaURL


@admin.register(models.MangaSeries)
class MangaSeriesAdmin(admin.ModelAdmin):
    inlines = [MangaURLInline]
    search_fields = ['title']


@admin.register(models.BakaSeries)
class BakaSeriesAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MangaSource)
class MangaSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MangaGenre)
class MangaGenreAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MangaPerson)
class MangaPersonAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MangaURL)
class MangaURLAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MangaSeriesKeyword)
class MangaKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'baka_series', 'score']


class MovieURLInline(admin.TabularInline):
    model = models.MovieURL


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieURLInline]
    search_fields = ['title']


@admin.register(models.VideoSource)
class VideoSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.IMDBMovie)
class IMDBMovieAdmin(admin.ModelAdmin):
    pass

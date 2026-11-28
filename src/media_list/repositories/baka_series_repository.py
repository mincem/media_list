from .external_item_repository import ExternalItemRepository
from ..models import MangaPerson, MangaGenre, BakaSeries, MangaKeyword


class BakaSeriesRepository(ExternalItemRepository):
    model = BakaSeries
    scalar_fields = (
        "baka_id", "title", "description", "status", "year", "original_publisher", "english_publisher",
    )

    def save_relations(self, instance, data):
        instance.genres.set(genres_from_names(data.get("genre_names") or []))
        instance.authors.set(people_from_names(data.get("author_names") or []))
        instance.artists.set(people_from_names(data.get("artist_names") or []))
        replace_keywords(data.get("keywords") or [], instance)


def people_from_names(names):
    return [MangaPerson.objects.get_or_create(name=name)[0] for name in names]


def genres_from_names(names):
    return [MangaGenre.objects.get_or_create(name=genre_name)[0] for genre_name in names]


def replace_keywords(keywords_data, baka_series):
    """Replaces the series' keyword links, so the scores of keywords that were already linked are updated too.

    Only the links (MangaSeriesKeyword) are deleted: the MangaKeyword rows are shared with other series.
    """
    baka_series.weighed_keywords.all().delete()
    for keyword_data in keywords_data:
        keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
        baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})

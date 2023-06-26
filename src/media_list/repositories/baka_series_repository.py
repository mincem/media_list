from ..models import MangaPerson, MangaGenre, BakaSeries, MangaKeyword


# pylint: disable=too-many-arguments
class BakaSeriesRepository:
    def create(self,
               baka_id=None,
               title=None,
               description=None,
               status=None,
               year=None,
               original_publisher=None,
               english_publisher=None,
               image=None,
               author_names=None,
               artist_names=None,
               genre_names=None,
               keywords=None,
               **_kwargs
               ):
        baka_series = BakaSeries.objects.create(
            baka_id=baka_id,
            title=title,
            description=description,
            status=status,
            year=year,
            original_publisher=original_publisher,
            english_publisher=english_publisher,
        )
        baka_series.genres.add(*genres_from_names(genre_names))
        baka_series.authors.add(*people_from_names(author_names))
        baka_series.artists.add(*people_from_names(artist_names))
        add_keywords(keywords, baka_series)
        if image is not None:
            baka_series.image.save(**image)
        return baka_series


def people_from_names(names):
    return [MangaPerson.objects.get_or_create(name=name)[0] for name in names]


def genres_from_names(names):
    return [MangaGenre.objects.get_or_create(name=genre_name)[0] for genre_name in names]


def add_keywords(keywords_data, baka_series):
    for keyword_data in keywords_data:
        keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
        baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})

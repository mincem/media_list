from ..models import IMDBMovie, VideoGenre, VideoCountry, VideoPerson, MovieCastMember


class IMDBMovieRepository:
    def create(self,
               imdb_id=None,
               title=None,
               plots=None,
               description=None,
               runtime=None,
               year=None,
               countries=None,
               genres=None,
               keywords=None,
               cast=None,
               directors=None,
               rating=None,
               image=None,
               ):
        imdb_movie = IMDBMovie.objects.create(
            imdb_id=imdb_id,
            title=title,
            description=description,
            runtime=runtime,
            year=year,
            rating=rating,
        )
        for plot in plots:
            imdb_movie.plots.create(text=plot)
        imdb_movie.countries.add(*countries_from_names(countries))
        imdb_movie.genres.add(*genres_from_names(genres))
        add_keywords(keywords, imdb_movie)
        add_cast(cast, imdb_movie)
        imdb_movie.directors.add(*directors_from_data(directors))
        if image is not None:
            imdb_movie.image.save(**image)
        return imdb_movie


def genres_from_names(names):
    return [VideoGenre.objects.get_or_create(name=genre_name)[0] for genre_name in names]


def countries_from_names(names):
    return [VideoCountry.objects.get_or_create(name=country_name)[0] for country_name in names]


def add_keywords(keyword_names, imdb_movie):
    for keyword_name in keyword_names:
        imdb_movie.keywords.get_or_create(name=keyword_name)


def add_cast(cast_data, imdb_movie):
    for cast_member_data in cast_data:
        cast_member = get_or_create_person(cast_member_data)
        MovieCastMember.objects.create(
            movie=imdb_movie,
            member=cast_member,
            role=cast_member_data["role"],
        )


def directors_from_data(directors_data):
    return [get_or_create_person(director_data) for director_data in directors_data]


def get_or_create_person(person_data):
    return VideoPerson.objects.get_or_create(
        imdb_id=person_data["id"],
        name=person_data["name"],
    )[0]

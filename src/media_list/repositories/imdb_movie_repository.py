from ..models import IMDBMovie, VideoGenre, VideoCountry, VideoPerson, VideoKeyword, MovieCastMember


# pylint: disable=too-many-arguments,too-many-positional-arguments
class IMDBMovieRepository:
    def create(self,
               imdb_id=None,
               tmdb_id=None,
               title=None,
               original_title=None,
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
               **_kwargs
               ):
        imdb_movie = IMDBMovie.objects.create(
            imdb_id=imdb_id,
            tmdb_id=tmdb_id,
            title=title,
            original_title=original_title,
            description=description,
            runtime=runtime,
            year=year,
            rating=rating,
        )
        for plot in plots:
            imdb_movie.plots.create(text=plot)
        imdb_movie.countries.add(*models_from_names(countries, VideoCountry))
        imdb_movie.genres.add(*models_from_names(genres, VideoGenre))
        imdb_movie.keywords.add(*models_from_names(keywords, VideoKeyword))
        add_cast(cast, imdb_movie)
        imdb_movie.directors.add(*directors_from_data(directors))
        if image is not None:
            imdb_movie.image.save(**image)
        return imdb_movie


def models_from_names(names, model):
    return [model.objects.get_or_create(name=name)[0] for name in names]


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
    """Finds a person by TMDB ID.

    Falls back to a person stored before TMDB (with no TMDB ID yet) with the same name, and gives them the TMDB ID.
    """
    tmdb_id, name = person_data["id"], person_data["name"]
    person = VideoPerson.objects.filter(tmdb_id=tmdb_id).first()
    if person is not None:
        return person
    person = VideoPerson.objects.filter(tmdb_id__isnull=True, name=name).first()
    if person is not None:
        person.tmdb_id = tmdb_id
        person.save()
        return person
    return VideoPerson.objects.create(tmdb_id=tmdb_id, name=name)

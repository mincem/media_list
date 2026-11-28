from .external_item_repository import ExternalItemRepository
from ..models import IMDBMovie, VideoGenre, VideoCountry, VideoPerson, VideoKeyword, MovieCastMember


class IMDBMovieRepository(ExternalItemRepository):
    model = IMDBMovie
    scalar_fields = (
        "imdb_id", "tmdb_id", "title", "original_title", "description", "runtime", "year", "rating",
    )

    def save_relations(self, instance, data):
        instance.plots.all().delete()
        for plot in data.get("plots") or []:
            instance.plots.create(text=plot)
        instance.countries.set(models_from_names(data.get("countries") or [], VideoCountry))
        instance.genres.set(models_from_names(data.get("genres") or [], VideoGenre))
        instance.keywords.set(models_from_names(data.get("keywords") or [], VideoKeyword))
        instance.ordered_cast.all().delete()
        add_cast(data.get("cast") or [], instance)
        instance.directors.set(directors_from_data(data.get("directors") or []))


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
    return VideoPerson.objects.from_credit(person_data["id"], person_data["name"])

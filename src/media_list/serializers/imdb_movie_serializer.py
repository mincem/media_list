import re
from datetime import timedelta


class IMDBMovieSerializer:
    def __init__(self, api_movie):
        self.api_movie = api_movie

    def serialize(self):
        return {
            "imdb_id": self.api_movie.movieID,
            "title": self.api_movie.get("title"),
            "plots": self.api_movie.get("plot", []),
            "description": self.parse_description(),
            "runtime": self.parse_runtime(),
            "year": self.api_movie.get("year"),
            "countries": self.api_movie.get("countries", []),
            "genres": self.api_movie.get("genres", []),
            "keywords": self.parse_keywords(),
            "cast": self.parse_cast(),
            "directors": self.parse_directors(),
            "rating": self.api_movie.get("rating"),
            "image_url": self.api_movie.get("full-size cover url"),
        }

    def parse_description(self):
        synopsis = self.api_movie.get("synopsis", [])[0]
        return re.sub("\.(?!\s|$)", ".\n\n", synopsis)

    def parse_runtime(self):
        runtimes = self.api_movie.get("runtime")
        if runtimes is None or not len(runtimes):
            return None
        return timedelta(minutes=int(runtimes[0]))

    def parse_cast(self):
        main_cast = self.api_movie.get("cast", [])[:10]
        return [parse_person_in_role(cast_member) for cast_member in main_cast]

    def parse_directors(self):
        return [parse_person(director) for director in (self.api_movie.get("directors", []))]

    def parse_keywords(self):
        return self.api_movie.get("keywords", [])[:10]


def parse_person(imdb_person):
    return {
        "id": imdb_person.personID,
        "name": imdb_person.get("name"),
    }


def parse_person_in_role(imdb_person):
    person = parse_person(imdb_person)
    person["role"] = parse_role(imdb_person)
    return person


def parse_role(imdb_person):
    if imdb_person.currentRole is None:
        return ""
    return str(imdb_person.currentRole)

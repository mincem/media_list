from datetime import timedelta

from ..integrations import imdb_number

TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/original"
MAX_CAST_MEMBERS = 10
MAX_KEYWORDS = 10


class TMDBMovieSerializer:
    """Maps a TMDB movie (details with appended credits and keywords) to the fields IMDBMovieRepository stores."""

    def __init__(self, api_movie):
        self.api_movie = api_movie

    def serialize(self):
        overview = self.api_movie.get("overview") or ""
        return {
            "imdb_id": imdb_number(self.api_movie.get("imdb_id")),
            "tmdb_id": self.api_movie.get("id"),
            "title": self.api_movie.get("title"),
            "original_title": self.api_movie.get("original_title") or "",
            "plots": [overview] if overview else [],
            "description": overview,
            "runtime": self.parse_runtime(),
            "year": self.parse_year(),
            "countries": names_of(self.api_movie.get("production_countries")),
            "genres": names_of(self.api_movie.get("genres")),
            "keywords": self.parse_keywords(),
            "cast": self.parse_cast(),
            "directors": self.parse_directors(),
            "rating": self.parse_rating(),
            "image_url": self.parse_image_url(),
        }

    def parse_runtime(self):
        runtime = self.api_movie.get("runtime")
        if not runtime:
            return None
        return timedelta(minutes=runtime)

    def parse_year(self):
        release_date = self.api_movie.get("release_date")
        if not release_date:
            return None
        return int(release_date[:4])

    def parse_keywords(self):
        keywords = (self.api_movie.get("keywords") or {}).get("keywords")
        return names_of(keywords)[:MAX_KEYWORDS]

    def parse_cast(self):
        cast = sorted(self.credits().get("cast") or [], key=lambda member: member.get("order", 0))
        return [parse_person_in_role(cast_member) for cast_member in cast[:MAX_CAST_MEMBERS]]

    def parse_directors(self):
        crew = self.credits().get("crew") or []
        return [parse_person(member) for member in crew if member.get("job") == "Director"]

    def parse_rating(self):
        return round(self.api_movie.get("vote_average") or 0, 1)

    def parse_image_url(self):
        poster_path = self.api_movie.get("poster_path")
        if not poster_path:
            return None
        return f"{TMDB_IMAGE_URL}{poster_path}"

    def credits(self):
        return self.api_movie.get("credits") or {}


def names_of(named_items):
    return [item["name"] for item in named_items or []]


def parse_person(tmdb_person):
    return {
        "id": tmdb_person["id"],
        "name": tmdb_person.get("name"),
    }


def parse_person_in_role(tmdb_person):
    person = parse_person(tmdb_person)
    person["role"] = tmdb_person.get("character") or ""
    return person

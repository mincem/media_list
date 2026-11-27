from .external_id_finder import ExternalIDFinder
from ..models import Movie
from ..utils import TMDBClient, imdb_number


class MovieIDFinder(ExternalIDFinder):
    """Finds a movie's IMDb ID with the TMDB search.

    Prefers a result whose title or original title equals the movie title, otherwise falls back to the first result.
    """

    def __init__(self, title, tmdb_client=None):
        super().__init__(title)
        self.tmdb_client = tmdb_client or TMDBClient()

    @classmethod
    def accepts(cls, item):
        return isinstance(item, Movie)

    def get_id(self):
        results = self.tmdb_client.search_movies(self.title)
        if not results:
            raise MovieSearchException(self.title)
        wanted = normalize_title(self.title)
        best = next((result for result in results if wanted in titles_of(result)), results[0])
        imdb_id = imdb_number(self.tmdb_client.movie_external_ids(best["id"]).get("imdb_id"))
        if imdb_id is None:
            raise MovieSearchException(self.title)
        return imdb_id


def titles_of(result):
    return {normalize_title(result.get("title")), normalize_title(result.get("original_title"))}


def normalize_title(title):
    return " ".join((title or "").casefold().split())


class MovieSearchException(Exception):
    def __init__(self, movie_title):
        super().__init__(f'Cannot find IMDb ID for movie "{movie_title}"')

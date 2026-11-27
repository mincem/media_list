import requests
from django.conf import settings


class TMDBClient:
    """Thin wrapper around the TMDB API v3: https://developer.themoviedb.org/reference"""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.TMDB_API_KEY

    def get(self, path, **params):
        response = requests.get(f"{self.BASE_URL}{path}", params={"api_key": self.api_key, **params}, timeout=30)
        response.raise_for_status()
        return response.json()

    def search_movies(self, title):
        return self.get("/search/movie", query=title)["results"]

    def movie(self, tmdb_id):
        """Movie details, including its IMDb ID, credits and keywords."""
        return self.get(f"/movie/{tmdb_id}", append_to_response="credits,keywords")

    def movie_external_ids(self, tmdb_id):
        return self.get(f"/movie/{tmdb_id}/external_ids")

    def find_movie_by_imdb_id(self, imdb_id):
        """TMDB ID of the movie with the given IMDb ID, or None."""
        results = self.get(f"/find/{imdb_tag(imdb_id)}", external_source="imdb_id")["movie_results"]
        return results[0]["id"] if results else None


def imdb_tag(imdb_id):
    """IMDb title ID as IMDb writes it: 34583 -> "tt0034583"."""
    return f"tt{str(imdb_id).zfill(7)}"


def imdb_number(imdb_tag_text):
    """Numeric part of an IMDb title ID: "tt0034583" -> 34583. None if there is no ID."""
    if not imdb_tag_text:
        return None
    return int(imdb_tag_text.removeprefix("tt"))

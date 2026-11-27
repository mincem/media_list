from .external_item_fetcher import ExternalItemFetcher
from ..models import Movie
from ..repositories import IMDBMovieRepository
from ..serializers.tmdb_movie_serializer import TMDBMovieSerializer
from ..integrations import TMDBClient


class ExternalMovieFetcher(ExternalItemFetcher):
    def __init__(self, item, tmdb_client=None, image_retriever_class=None):
        super().__init__(item, image_retriever_class)
        self.tmdb_client = tmdb_client or TMDBClient()

    @classmethod
    def accepts(cls, item):
        return isinstance(item, Movie)

    def fetch(self):
        tmdb_id = self.tmdb_client.find_movie_by_imdb_id(self.item.imdb_id)
        if tmdb_id is None:
            raise MovieNotFoundException(self.item.imdb_id)
        api_movie = self.tmdb_client.movie(tmdb_id)
        movie_dict = TMDBMovieSerializer(api_movie).serialize()
        movie_dict["imdb_id"] = movie_dict["imdb_id"] or self.item.imdb_id
        image_url = movie_dict.pop("image_url")
        if image_url is not None:
            movie_dict["image"] = self.image_retriever_class(image_url).fetch()
        return IMDBMovieRepository().create(**movie_dict)


class MovieNotFoundException(Exception):
    def __init__(self, imdb_id):
        super().__init__(f"Cannot find a TMDB movie with IMDb ID {imdb_id}")

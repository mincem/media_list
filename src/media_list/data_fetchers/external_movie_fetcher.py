from imdb import Cinemagoer

from .external_item_fetcher import ExternalItemFetcher
from ..models import Movie
from ..repositories import IMDBMovieRepository
from ..serializers import IMDBMovieSerializer


class ExternalMovieFetcher(ExternalItemFetcher):
    def __init__(self, item, imdb_access=None, image_retriever_class=None):
        super().__init__(item, image_retriever_class)
        self.imdb_access = imdb_access or Cinemagoer()

    @classmethod
    def accepts(cls, item):
        return isinstance(item, Movie)

    def fetch(self):
        api_movie = self.imdb_access.get_movie(self.item.imdb_id, info=["main", "plot", "keywords", "akas"])
        movie_dict = IMDBMovieSerializer(api_movie).serialize()
        image_url = movie_dict.pop("image_url")
        if image_url is not None:
            movie_dict["image"] = self.image_retriever_class(image_url).fetch()
        return IMDBMovieRepository().create(**movie_dict)

import imdb

from .external_item_fetcher import ExternalItemFetcher
from ..serializers import IMDBMovieSerializer
from ..repositories import IMDBMovieRepository


class ExternalMovieFetcher(ExternalItemFetcher):
    def __init__(self, item, imdb_access=None, image_retriever_class=None):
        super().__init__(item, image_retriever_class)
        self.imdb_access = imdb_access or imdb.IMDb()

    def fetch(self):
        api_movie = self.imdb_access.get_movie(self.item.imdb_id, info=["main", "plot", "keywords", "akas"])
        movie_dict = IMDBMovieSerializer(api_movie).serialize()
        image_url = movie_dict.pop("image_url")
        if image_url is not None:
            movie_dict["image"] = self.image_retriever_class(image_url).fetch()
        return IMDBMovieRepository().create(**movie_dict)

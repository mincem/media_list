import imdb

from .external_item_fetcher import ExternalItemFetcher
from ..serializers import IMDBMovieSerializer
from ..repositories import IMDBMovieRepository
from ..utils import ImageRetriever


class ExternalMovieFetcher(ExternalItemFetcher):
    def __init__(self, item, imdb_access=None, image_retriever_class=None):
        super().__init__(item)
        if not self.item.imdb_id:
            raise Exception("Missing IMDb ID")
        self.imdb_access = imdb_access or imdb.IMDb()
        self.image_retriever_class = image_retriever_class or ImageRetriever

    def fetch(self):
        api_movie = self.imdb_access.get_movie(self.item.imdb_id, info=["main", "plot", "keywords", "akas"])
        movie_dict = IMDBMovieSerializer(api_movie).serialize()
        image_url = movie_dict.pop("image_url")
        if image_url is not None:
            movie_dict["image"] = self.image_retriever_class(image_url).fetch()
        return IMDBMovieRepository().create(**movie_dict)

import imdb

from ..serializers import IMDBMovieSerializer
from ..repositories import IMDBMovieRepository
from ..utils import ImageRetriever


class MovieDataFetcher:
    def __init__(self, movie, imdb_access=None, image_retriever_class=None):
        if not movie.imdb_id:
            raise Exception("Missing IMDb ID")
        self.movie = movie
        self.imdb_access = imdb_access or imdb.IMDb()
        self.image_retriever_class = image_retriever_class or ImageRetriever

    def get_data(self):
        api_movie = self.imdb_access.get_movie(self.movie.imdb_id, info=["main", "plot", "keywords"])
        movie_dict = IMDBMovieSerializer(api_movie).serialize()
        image_url = movie_dict.pop("image_url")
        if image_url is not None:
            movie_dict["image"] = self.image_retriever_class(image_url).fetch()
        return IMDBMovieRepository().create(**movie_dict)

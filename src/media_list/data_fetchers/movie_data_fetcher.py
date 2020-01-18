import imdb

from ..serializers import IMDBMovieSerializer
from ..repositories import IMDBMovieRepository


class MovieDataFetcher:
    def __init__(self, movie, imdb_access=None):
        if not movie.imdb_id:
            raise Exception("Missing IMDb ID")
        self.movie = movie
        self.imdb_access = imdb_access or imdb.IMDb()

    def get_data(self):
        api_movie = self.imdb_access.get_movie(self.movie.imdb_id, info=["main", "plot", "keywords"])
        movie_dict = IMDBMovieSerializer(api_movie).serialize()
        return IMDBMovieRepository().create(**movie_dict)

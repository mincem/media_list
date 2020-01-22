import imdb

from . import ExternalIDFinder


class MovieIDFinder(ExternalIDFinder):
    def __init__(self, series_title, imdb_access=None):
        super().__init__(series_title)
        self.imdb_access = imdb_access or imdb.IMDb()

    def get_id(self):
        movie_results = self.imdb_access.search_movie(self.series_title)
        return next(result.movieID for result in movie_results if is_a_movie(result))


def is_a_movie(imdb_object):
    return imdb_object['kind'] == 'movie'
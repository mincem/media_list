from django.test import TestCase

from ...id_finders import MovieIDFinder, MovieSearchException


class MockTMDBClient:
    def __init__(self, search_results, imdb_ids=None):
        self.search_results = search_results
        self.imdb_ids = imdb_ids or {}
        self.searched_titles = []

    def search_movies(self, title):
        self.searched_titles.append(title)
        return self.search_results

    def movie_external_ids(self, tmdb_id):
        return {"id": tmdb_id, "imdb_id": self.imdb_ids.get(tmdb_id)}


class TestMovieIDFinder(TestCase):
    def test_get_imdb_id_of_first_result(self):
        client = MockTMDBClient(
            [{"id": 77, "title": "Memento Mori"}, {"id": 99, "title": "Other"}],
            {77: "tt0209144", 99: "tt0000099"},
        )
        self.assertEqual(209144, MovieIDFinder("Memento", client).get_id())
        self.assertEqual(["Memento"], client.searched_titles)

    def test_prefer_result_with_same_title(self):
        client = MockTMDBClient(
            [{"id": 1, "title": "Memento Mori"}, {"id": 77, "title": "Memento"}],
            {1: "tt0000001", 77: "tt0209144"},
        )
        self.assertEqual(209144, MovieIDFinder("  memento ", client).get_id())

    def test_prefer_result_with_same_original_title(self):
        client = MockTMDBClient(
            [
                {"id": 1, "title": "Spirited Away 2"},
                {"id": 129, "title": "Spirited Away", "original_title": "千と千尋の神隠し"},
            ],
            {1: "tt0000001", 129: "tt0245429"},
        )
        self.assertEqual(245429, MovieIDFinder("千と千尋の神隠し", client).get_id())

    def test_no_results(self):
        with self.assertRaises(MovieSearchException) as context_manager:
            MovieIDFinder("Nothing", MockTMDBClient([])).get_id()
        self.assertEqual('Cannot find IMDb ID for movie "Nothing"', str(context_manager.exception))

    def test_result_without_imdb_id(self):
        client = MockTMDBClient([{"id": 5, "title": "Obscure"}])
        with self.assertRaises(MovieSearchException):
            MovieIDFinder("Obscure", client).get_id()

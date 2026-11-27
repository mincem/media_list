from unittest import mock

from django.test import TestCase, override_settings

from ..utils import TMDBClient, imdb_number, imdb_tag


def mock_response(json_data):
    response = mock.Mock()
    response.json.return_value = json_data
    return response


class TestIMDbIDs(TestCase):
    def test_imdb_tag(self):
        self.assertEqual("tt0034583", imdb_tag(34583))
        self.assertEqual("tt10872600", imdb_tag(10872600))

    def test_imdb_number(self):
        self.assertEqual(34583, imdb_number("tt0034583"))
        self.assertEqual(10872600, imdb_number("tt10872600"))
        self.assertIsNone(imdb_number(None))
        self.assertIsNone(imdb_number(""))


@mock.patch("media_list.utils.tmdb_client.requests.get")
class TestTMDBClient(TestCase):
    @override_settings(TMDB_API_KEY="settings-key")
    def test_reads_api_key_from_settings(self, get):
        get.return_value = mock_response({"results": []})
        TMDBClient().search_movies("Memento")
        self.assertEqual("settings-key", get.call_args.kwargs["params"]["api_key"])

    def test_search_movies(self, get):
        get.return_value = mock_response({"results": [{"id": 77}]})
        self.assertEqual([{"id": 77}], TMDBClient("key").search_movies("Memento"))
        get.assert_called_once_with(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": "key", "query": "Memento"},
            timeout=30,
        )

    def test_movie_appends_credits_and_keywords(self, get):
        get.return_value = mock_response({"id": 77})
        TMDBClient("key").movie(77)
        get.assert_called_once_with(
            "https://api.themoviedb.org/3/movie/77",
            params={"api_key": "key", "append_to_response": "credits,keywords"},
            timeout=30,
        )

    def test_find_movie_by_imdb_id(self, get):
        get.return_value = mock_response({"movie_results": [{"id": 77}], "tv_results": []})
        self.assertEqual(77, TMDBClient("key").find_movie_by_imdb_id(209144))
        get.assert_called_once_with(
            "https://api.themoviedb.org/3/find/tt0209144",
            params={"api_key": "key", "external_source": "imdb_id"},
            timeout=30,
        )

    def test_find_movie_by_imdb_id_without_results(self, get):
        get.return_value = mock_response({"movie_results": []})
        self.assertIsNone(TMDBClient("key").find_movie_by_imdb_id(1))

    def test_raises_on_http_errors(self, get):
        get.return_value = mock_response({})
        get.return_value.raise_for_status.side_effect = Exception("401 Unauthorized")
        with self.assertRaises(Exception):
            TMDBClient("key").search_movies("Memento")

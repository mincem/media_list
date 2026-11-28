from unittest import mock

from django.core.files.base import ContentFile
from django.test import TestCase

from ..serializers.test_tmdb_movie_serializer import sample_movie
from ...data_fetchers import ExternalMovieFetcher
from ...data_fetchers.external_movie_fetcher import MovieNotFoundException
from ...models import Movie


class MockTMDBClient:
    def __init__(self, tmdb_id=77, api_movie=None):
        self.tmdb_id = tmdb_id
        self.api_movie = api_movie if api_movie is not None else sample_movie()
        self.found_imdb_ids = []
        self.fetched_tmdb_ids = []

    def find_movie_by_imdb_id(self, imdb_id):
        self.found_imdb_ids.append(imdb_id)
        return self.tmdb_id

    def movie(self, tmdb_id):
        self.fetched_tmdb_ids.append(tmdb_id)
        return self.api_movie


class MockImageRetriever:
    fetched_urls = []

    def __init__(self, image_url):
        self.image_url = image_url

    def fetch(self):
        MockImageRetriever.fetched_urls.append(self.image_url)
        return {"name": "poster.jpg", "content": ContentFile(b"image")}


class TestExternalMovieFetcher(TestCase):
    def setUp(self):
        MockImageRetriever.fetched_urls = []
        self.movie = Movie(title="Memento", imdb_id=209144, interest=50)

    def fetch(self, client):
        fetcher = ExternalMovieFetcher(self.movie, tmdb_client=client, image_retriever_class=MockImageRetriever)
        with mock.patch("django.core.files.storage.FileSystemStorage.save", return_value="movie_images/poster.jpg"):
            return fetcher.fetch()

    def test_looks_up_tmdb_movie_by_imdb_id(self):
        client = MockTMDBClient()
        self.fetch(client)
        self.assertEqual([209144], client.found_imdb_ids)
        self.assertEqual([77], client.fetched_tmdb_ids)

    def test_stores_movie_data(self):
        imdb_movie = self.fetch(MockTMDBClient())
        self.assertEqual(209144, imdb_movie.imdb_id)
        self.assertEqual(77, imdb_movie.tmdb_id)
        self.assertEqual("Memento", imdb_movie.title)
        self.assertEqual("Guy Pearce", str(imdb_movie.ordered_cast.first()))
        self.assertTrue(imdb_movie.description.startswith("Leonard Shelby is tracking down"))
        self.assertEqual(imdb_movie.description, str(imdb_movie.plots.first()))

    def test_fetches_poster(self):
        imdb_movie = self.fetch(MockTMDBClient())
        self.assertEqual(["https://image.tmdb.org/t/p/original/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg"],
                         MockImageRetriever.fetched_urls)
        self.assertEqual("movie_images/poster.jpg", imdb_movie.image.name)

    def test_keeps_item_imdb_id_when_tmdb_has_none(self):
        api_movie = sample_movie()
        api_movie["imdb_id"] = None
        imdb_movie = self.fetch(MockTMDBClient(api_movie=api_movie))
        self.assertEqual(209144, imdb_movie.imdb_id)

    def test_movie_not_found(self):
        with self.assertRaises(MovieNotFoundException) as context_manager:
            self.fetch(MockTMDBClient(tmdb_id=None))
        self.assertEqual("Cannot find a TMDB movie with IMDb ID 209144", str(context_manager.exception))

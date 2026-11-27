import datetime
from unittest import mock

from django.core.files.base import File
from django.test import TestCase

from ..models import VideoPerson
from ..repositories import IMDBMovieRepository

casablanca_data = {
    "imdb_id": 34583,
    "tmdb_id": 289,
    "title": "Casablanca",
    "original_title": "Casablanca",
    "plots": [
        "A cynical American expatriate struggles to decide",
        "The story of Rick Blaine, a cynical world-weary",
        "In World War II Casablanca, Rick Blaine, exiled",
        "During World War II, Europeans who were fleeing",
        "Rick Blaine, who owns a nightclub in Casablanca",
    ],
    "description": "In the early years of World War II, December 1941",
    "runtime": datetime.timedelta(seconds=6120),
    "year": 1942,
    "countries": ["United States"],
    "genres": ["Drama", "Romance", "War"],
    "keywords": [
        "nazi", "anti-nazi", "casablanca-morocco", "french-morocco", "1940s", "lovers-reunited", "love-triangle",
        "police", "nightclub", "escape"
    ],
    "cast": [
        {"id": 4110, "name": "Humphrey Bogart", "role": "Rick Blaine"},
        {"id": 4111, "name": "Ingrid Bergman", "role": "Ilsa Lund"},
        {"id": 4112, "name": "Paul Henreid", "role": "Victor Laszlo"},
        {"id": 4113, "name": "Claude Rains", "role": "Captain Louis Renault"},
        {"id": 4114, "name": "Conrad Veidt", "role": "Major Heinrich Strasser"},
        {"id": 4115, "name": "Sydney Greenstreet", "role": "Signor Ferrari"},
        {"id": 2094, "name": "Peter Lorre", "role": "Ugarte"},
        {"id": 4117, "name": "S.Z. Sakall", "role": "Carl"},
        {"id": 4118, "name": "Madeleine Lebeau", "role": "Yvonne"},
        {"id": 4119, "name": "Dooley Wilson", "role": "Sam"},
    ],
    "directors": [{"id": 10541, "name": "Michael Curtiz"}],
    "rating": 8.5,
    "image": {
        "name": "FileMock",
        "content": mock.MagicMock(spec=File, name="FileMock"),
    },
}


class IMDBMovieRepositoryTests(TestCase):
    def setUp(self):
        self.imdb_movie = IMDBMovieRepository().create(**casablanca_data)

    def test_store_correct_imdb_id(self):
        self.assertEqual(34583, self.imdb_movie.imdb_id)

    def test_store_correct_title(self):
        self.assertEqual("Casablanca", self.imdb_movie.title)

    def test_store_correct_tmdb_id(self):
        self.assertEqual(289, self.imdb_movie.tmdb_id)

    def test_store_correct_original_title(self):
        self.assertEqual("Casablanca", self.imdb_movie.original_title)

    def test_store_correct_plots(self):
        self.assertEqual("During World War II, Europeans who were fleeing", str(self.imdb_movie.plots.all()[3]))

    def test_store_correct_description(self):
        self.assertEqual("In the early years of World War II, December 1941", self.imdb_movie.description)

    def test_store_correct_runtime(self):
        self.assertEqual(datetime.timedelta(seconds=6120), self.imdb_movie.runtime)

    def test_store_correct_year(self):
        self.assertEqual(1942, self.imdb_movie.year)

    def test_store_correct_countries(self):
        self.assertEqual("United States", str(self.imdb_movie.countries.first()))

    def test_store_correct_genres(self):
        self.assertSetEqual({"Drama", "Romance", "War"}, {str(genre) for genre in self.imdb_movie.genres.all()})

    def test_store_correct_keywords(self):
        self.assertIn("french-morocco", {str(keyword) for keyword in self.imdb_movie.keywords.all()})
        self.assertEqual(10, self.imdb_movie.keywords.count())

    def test_store_correct_cast(self):
        self.assertEqual("Humphrey Bogart", str(self.imdb_movie.ordered_cast.first()))
        self.assertEqual("Rick Blaine", self.imdb_movie.ordered_cast.first().role)
        self.assertEqual(4110, self.imdb_movie.ordered_cast.first().member.tmdb_id)
        self.assertEqual(10, self.imdb_movie.ordered_cast.count())

    def test_store_correct_directors(self):
        self.assertEqual("Michael Curtiz", str(self.imdb_movie.directors.first()))

    def test_store_correct_rating(self):
        self.assertEqual(8.5, self.imdb_movie.rating)

    def test_store_image_in_correct_path(self):
        self.assertIn("/media/movie_images/", self.imdb_movie.image.url)


class IMDBMovieRepositoryPeopleTests(TestCase):
    def test_reuse_person_with_same_tmdb_id(self):
        IMDBMovieRepository().create(**casablanca_data)
        IMDBMovieRepository().create(**casablanca_data)
        self.assertEqual(1, VideoPerson.objects.filter(tmdb_id=4110).count())

    def test_give_tmdb_id_to_person_stored_before_tmdb(self):
        legacy_person = VideoPerson.objects.create(imdb_id=7, name="Humphrey Bogart")
        imdb_movie = IMDBMovieRepository().create(**casablanca_data)
        legacy_person.refresh_from_db()
        self.assertEqual(4110, legacy_person.tmdb_id)
        self.assertEqual(legacy_person, imdb_movie.ordered_cast.first().member)
        self.assertEqual(1, VideoPerson.objects.filter(name="Humphrey Bogart").count())

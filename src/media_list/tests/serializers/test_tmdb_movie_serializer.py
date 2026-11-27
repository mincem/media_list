import json
from datetime import timedelta

from django.test import TestCase

from .. import SAMPLES_DIR
from ...serializers.tmdb_movie_serializer import TMDBMovieSerializer

SAMPLE_PATH = SAMPLES_DIR / "sample_tmdb_movie.json"


def sample_movie():
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


class TestTMDBMovieSerializer(TestCase):
    def setUp(self):
        self.movie = TMDBMovieSerializer(sample_movie()).serialize()

    def test_ids(self):
        self.assertEqual(209144, self.movie["imdb_id"])
        self.assertEqual(77, self.movie["tmdb_id"])

    def test_titles(self):
        self.assertEqual("Memento", self.movie["title"])
        self.assertEqual("Memento", self.movie["original_title"])

    def test_plot_and_description_are_the_overview(self):
        overview = sample_movie()["overview"]
        self.assertEqual([overview], self.movie["plots"])
        self.assertEqual(overview, self.movie["description"])

    def test_runtime(self):
        self.assertEqual(timedelta(minutes=113), self.movie["runtime"])

    def test_year(self):
        self.assertEqual(2000, self.movie["year"])

    def test_countries(self):
        self.assertEqual(["United States of America"], self.movie["countries"])

    def test_genres(self):
        self.assertEqual(["Mystery", "Thriller"], self.movie["genres"])

    def test_keywords_are_limited_to_ten(self):
        self.assertEqual(10, len(self.movie["keywords"]))
        self.assertEqual("tattoo", self.movie["keywords"][0])

    def test_cast_is_ordered_and_limited_to_ten(self):
        cast = self.movie["cast"]
        self.assertEqual(10, len(cast))
        self.assertEqual({"id": 529, "name": "Guy Pearce", "role": "Leonard"}, cast[0])
        self.assertEqual("Carrie-Anne Moss", cast[1]["name"])
        self.assertEqual("Callum Keith Rennie", cast[9]["name"])

    def test_directors_only_include_the_director_job(self):
        self.assertEqual([{"id": 525, "name": "Christopher Nolan"}], self.movie["directors"])

    def test_rating_is_rounded(self):
        self.assertEqual(8.2, self.movie["rating"])

    def test_image_url(self):
        self.assertEqual("https://image.tmdb.org/t/p/original/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg", self.movie["image_url"])


class TestTMDBMovieSerializerWithMissingData(TestCase):
    def setUp(self):
        self.movie = TMDBMovieSerializer({"id": 1, "title": "Unknown"}).serialize()

    def test_defaults(self):
        self.assertIsNone(self.movie["imdb_id"])
        self.assertEqual("", self.movie["original_title"])
        self.assertEqual([], self.movie["plots"])
        self.assertEqual("", self.movie["description"])
        self.assertIsNone(self.movie["runtime"])
        self.assertIsNone(self.movie["year"])
        self.assertEqual([], self.movie["countries"])
        self.assertEqual([], self.movie["genres"])
        self.assertEqual([], self.movie["keywords"])
        self.assertEqual([], self.movie["cast"])
        self.assertEqual([], self.movie["directors"])
        self.assertEqual(0, self.movie["rating"])
        self.assertIsNone(self.movie["image_url"])

    def test_cast_member_without_character_has_empty_role(self):
        movie = TMDBMovieSerializer({"credits": {"cast": [{"id": 1, "name": "Someone", "character": None}]}})
        self.assertEqual("", movie.serialize()["cast"][0]["role"])

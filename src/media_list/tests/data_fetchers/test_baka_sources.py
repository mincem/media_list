import json
from unittest import TestCase as SimpleTestCase

import requests
from django.test import TestCase

from .. import SAMPLES_DIR
from .test_external_manga_fetcher import MockIDResolver, MockImageRetriever, MockManga, ShingekiMockBakaRetriever
from ...data_fetchers import ExternalMangaFetcher
from ...data_fetchers.baka_sources import BakaApiSource, BakaScraperSource, BakaSourceError, fetch_from_sources
from ...integrations import BakaApiParser
from ...serializers.baka_serializer import BakaSerializer

SAMPLE_API_PATH = SAMPLES_DIR / "sample_baka_api.json"
SHINGEKI_CODE = "aqw5kar"
SHINGEKI_API_ID = 23393951235

api_shingeki_genres = {
    "Action", "Drama", "Fantasy", "Horror", "Mature", "Mystery", "Psychological", "Shounen", "Supernatural", "Tragedy",
}
api_shingeki_english_publisher = (
    "Kodansha USA (34 Vols - Complete | Colossal Edition [5-in-1] 7 Vols - Complete; print| "
    "Omnibus Edition [3-in-1] 12 Vols - Complete; print)"
)


def load_sample_json():
    with open(SAMPLE_API_PATH, encoding="utf-8") as json_file:
        return json.load(json_file)


class MockBakaApiRetriever:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requested_codes = []

    def get(self, baka_code):
        self.requested_codes.append(baka_code)
        if self.error is not None:
            raise self.error
        return self.response if self.response is not None else load_sample_json()


class BakaApiSerializerTests(SimpleTestCase):
    def test_api_series_id_is_base_36_value_of_code(self):
        self.assertEqual(SHINGEKI_API_ID, BakaSerializer.api_series_id(SHINGEKI_CODE))

    def test_api_url(self):
        self.assertEqual(
            f"https://api.mangaupdates.com/v1/series/{SHINGEKI_API_ID}",
            BakaSerializer.api_url(SHINGEKI_CODE),
        )


class BakaApiParserTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = BakaApiParser(load_sample_json(), baka_id=SHINGEKI_CODE).parse()

    def test_same_keys_as_scraper(self):
        self.assertSetEqual(
            {"baka_id", "title", "genre_names", "keywords", "description", "status", "author_names",
             "artist_names", "year", "original_publisher", "english_publisher", "image_url"},
            set(self.data),
        )

    def test_baka_id(self):
        self.assertEqual(SHINGEKI_CODE, self.data["baka_id"])

    def test_title(self):
        self.assertEqual("Shingeki no Kyojin", self.data["title"])

    def test_genres(self):
        self.assertSetEqual(api_shingeki_genres, set(self.data["genre_names"]))

    def test_keywords_use_votes_as_score(self):
        keywords = {keyword["name"]: keyword["score"] for keyword in self.data["keywords"]}
        self.assertEqual(220, len(keywords))
        self.assertEqual(164, keywords["Giant/s"])
        self.assertEqual(7, keywords["Clean Freak"])  # votes, not votes_plus - votes_minus (8 - 3)

    def test_description_keeps_markdown(self):
        self.assertTrue(self.data["description"].startswith("From Kodansha:"))
        self.assertIn("**Original Manga:**", self.data["description"])

    def test_status(self):
        self.assertEqual("34 Volumes (Complete)", self.data["status"])

    def test_authors_and_artists_split_by_type(self):
        self.assertEqual(["ISAYAMA Hajime"], self.data["author_names"])
        self.assertEqual(["ISAYAMA Hajime"], self.data["artist_names"])

    def test_year_is_int(self):
        self.assertEqual(2009, self.data["year"])

    def test_original_publisher_without_notes(self):
        self.assertEqual("Kodansha", self.data["original_publisher"])

    def test_english_publisher_keeps_full_notes(self):
        self.assertEqual(api_shingeki_english_publisher, self.data["english_publisher"])

    def test_image_url(self):
        self.assertEqual("https://cdn.mangaupdates.com/image/i424594.png", self.data["image_url"])


class BakaApiParserEdgeCaseTests(SimpleTestCase):
    def parse(self, **fields):
        return BakaApiParser({"title": "Some title", **fields}).parse()

    def test_missing_optional_fields(self):
        data = self.parse(image=None, year="", genres=None, categories=None, authors=None, publishers=None)
        self.assertIsNone(data["year"])
        self.assertIsNone(data["image_url"])
        self.assertEqual([], data["genre_names"])
        self.assertEqual([], data["keywords"])
        self.assertEqual([], data["author_names"])
        self.assertEqual("", data["original_publisher"])
        self.assertEqual("", data["description"])

    def test_multiple_publishers_of_same_type_are_joined(self):
        data = self.parse(publishers=[
            {"publisher_name": "A", "type": "English", "notes": "1 Vol"},
            {"publisher_name": "B", "type": "English", "notes": ""},
            {"publisher_name": "C", "type": "Original", "notes": ""},
        ])
        self.assertEqual("A (1 Vol), B", data["english_publisher"])
        self.assertEqual("C", data["original_publisher"])


class ApiFetcherTests(TestCase):
    def fetch(self, manga, api_retriever, scraper_retriever=None):
        scraper_retriever = scraper_retriever or ShingekiMockBakaRetriever()
        baka_series = ExternalMangaFetcher(
            item=manga,
            sources=[BakaApiSource(api_retriever), BakaScraperSource(scraper_retriever)],
            image_retriever_class=MockImageRetriever,
        ).fetch()
        return baka_series, scraper_retriever

    def test_code_is_fetched_from_api(self):
        api_retriever = MockBakaApiRetriever()
        baka_series, scraper_retriever = self.fetch(MockManga(baka_id=SHINGEKI_CODE), api_retriever)
        self.assertEqual([SHINGEKI_CODE], api_retriever.requested_codes)
        self.assertEqual([], scraper_retriever.requested_urls)
        self.assertEqual(SHINGEKI_CODE, baka_series.baka_id)
        self.assertEqual("34 Volumes (Complete)", baka_series.status)
        self.assertEqual(api_shingeki_english_publisher, baka_series.english_publisher)
        self.assertSetEqual(api_shingeki_genres, {str(genre) for genre in baka_series.genres.all()})
        self.assertEqual(220, baka_series.keywords.count())

    def test_falls_back_to_scraper_when_api_request_fails(self):
        api_retriever = MockBakaApiRetriever(error=requests.ConnectionError("API down"))
        with self.assertLogs("media_list.data_fetchers.baka_sources", level="WARNING"):
            baka_series, scraper_retriever = self.fetch(MockManga(baka_id=SHINGEKI_CODE), api_retriever)
        self.assertEqual([SHINGEKI_CODE], api_retriever.requested_codes)
        self.assertEqual([f"https://www.mangaupdates.com/series/{SHINGEKI_CODE}"], scraper_retriever.requested_urls)
        self.assertEqual("28 Volumes (Ongoing)", baka_series.status)  # From the HTML sample

    def test_falls_back_to_scraper_when_api_response_is_unexpected(self):
        api_retriever = MockBakaApiRetriever(response={"unexpected": "shape"})
        with self.assertLogs("media_list.data_fetchers.baka_sources", level="WARNING"):
            baka_series, _scraper_retriever = self.fetch(MockManga(baka_id=SHINGEKI_CODE), api_retriever)
        self.assertEqual("28 Volumes (Ongoing)", baka_series.status)

    def test_numeric_id_is_resolved_and_fetched_from_api(self):
        api_retriever = MockBakaApiRetriever()
        manga = MockManga(baka_id="1234567")
        baka_series = ExternalMangaFetcher(
            item=manga,
            sources=[BakaApiSource(api_retriever), BakaScraperSource(ShingekiMockBakaRetriever())],
            image_retriever_class=MockImageRetriever,
            id_resolver=MockIDResolver(code=SHINGEKI_CODE),
        ).fetch()
        self.assertEqual([SHINGEKI_CODE], api_retriever.requested_codes)
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)
        self.assertEqual(SHINGEKI_CODE, baka_series.baka_id)

    def test_scraper_keyword_scores_are_ints_like_the_api(self):
        result = BakaScraperSource(ShingekiMockBakaRetriever()).fetch(SHINGEKI_CODE)
        scores = {keyword["name"]: keyword["score"] for keyword in result.series_data["keywords"]}
        self.assertEqual(153, scores["Giant/s"])


class FetchFromSourcesTests(SimpleTestCase):
    def test_no_accepting_source_raises(self):
        with self.assertRaises(BakaSourceError):
            fetch_from_sources("1234567", sources=[BakaApiSource(MockBakaApiRetriever())])

    def test_last_error_is_raised_when_all_sources_fail(self):
        api_retriever = MockBakaApiRetriever(error=requests.Timeout("slow"))
        with self.assertLogs("media_list.data_fetchers.baka_sources", level="WARNING"):
            with self.assertRaises(BakaSourceError):
                fetch_from_sources(SHINGEKI_CODE, sources=[BakaApiSource(api_retriever)])

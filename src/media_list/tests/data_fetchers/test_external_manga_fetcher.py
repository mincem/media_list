from unittest import mock

from django.core.files.base import File
from django.test import TestCase

from .. import SAMPLES_DIR
from ...data_fetchers import ExternalMangaFetcher
from ...data_fetchers.baka_sources import BakaPage, BakaScraperSource

MOCK_BAKA_ID = "1234567"
MOCK_BAKA_CODE = "a1b2c3d4"
MOCK_REDIRECT_URL = f"https://www.mangaupdates.com/series/{MOCK_BAKA_CODE}/shingeki-no-kyojin"
FMP_SIGMA_BAKA_ID = 913

shingeki_authors = {"ISAYAMA Hajime"}
shingeki_artists = {"ISAYAMA Hajime"}
shingeki_title = "Shingeki no Kyojin"
shingeki_year = 2009
shingeki_genres = {"Action", "Drama", "Fantasy", "Horror", "Mature", "Mystery", "Shounen", "Supernatural", "Tragedy"}
shingeki_keywords = {
    'Giant/s': 153, 'Military': 144, 'Mysterious Power/s': 137, 'Survival': 136, 'Dead Family Member/s': 134,
    'Strong Female Lead': 132, 'Hidden Power/s': 131, 'Revenge': 129, 'Apocalypse': 128, 'Teamwork': 123,
}
shingeki_status = "28 Volumes (Ongoing)"
shingeki_original_publisher = "Kodansha"
shingeki_english_publisher = "Kodansha Comics (26 Volumes - Ongoing)"
shingeki_description = \
    "In a world entirely ruled by giants, the human race, which has turned into their food, has surrounded its " \
    "residential zones with immense walls, which both prevent their freedom outside the walls and protect them from " \
    "incursions. However, as a result of the appearance of supergiants who cross the wall, a desperate struggle" \
    " begins and the young heroes, who have lost their parents, fight the giant as a training corps, with a view" \
    " to regaining their freedom. Note: Won the Kodansha Manga Award in the shōnen category in 2011, was nominated" \
    " for the 4th annual Manga Taishō award and also for the the 16th and 18th annual Tezuka Osamu Cultural Prize."

princess_authors = {'SAKAKI Ichiro'}
princess_artists = {'SOGABE Toshinori', 'YUKINOBU Azumi', 'YABUKI Gou'}


class MockBakaRetriever:
    """Serves a sample page. Pass final_url to simulate a redirect; by default the URL is returned unchanged."""
    sample_path = None

    def __init__(self, final_url=None):
        self.final_url = final_url
        self.requested_urls = []

    def get(self, baka_url):
        self.requested_urls.append(baka_url)
        with open(self.sample_path, "rb") as html_file:
            return BakaPage(html=html_file.read(), url=self.final_url or baka_url)


class ShingekiMockBakaRetriever(MockBakaRetriever):
    sample_path = SAMPLES_DIR / "sample_baka.html"


class PrincessMockBakaRetriever(MockBakaRetriever):
    sample_path = SAMPLES_DIR / "sample_baka_2.html"


class MockImageRetriever:
    def __init__(self, _image_url):
        pass

    def fetch(self):
        return {
            "name": 'FileMock',
            "content": mock.MagicMock(spec=File, name='FileMock'),
        }


class MockManga:
    def __init__(self, baka_id=MOCK_BAKA_ID):
        self.baka_id = baka_id

    @property
    def external_id(self):
        return self.baka_id


class ExternalMangaFetcherTests(TestCase):
    def setUp(self):
        self.baka_series = ExternalMangaFetcher(
            item=MockManga(),
            sources=[BakaScraperSource(ShingekiMockBakaRetriever())],
            image_retriever_class=MockImageRetriever,
        ).fetch()

    # def test_pending(self):
    #     parser = ExternalMangaFetcher(FMP_SIGMA_BAKA_ID, MockBakaRetriever())
    #     print(parser.display_parsed_data())  # Full Metal Panic Sigma (check sigma char)
    #     self.assertTrue(False)

    def test_store_correct_baka_id(self):
        self.assertEqual(MOCK_BAKA_ID, self.baka_series.baka_id)

    def test_store_correct_title(self):
        self.assertEqual(shingeki_title, self.baka_series.title)

    def test_store_correct_genres(self):
        baka_series_genres = {str(genre) for genre in self.baka_series.genres.all()}
        self.assertSetEqual(shingeki_genres, baka_series_genres)

    def test_store_correct_keywords(self):
        baka_series_keywords = {str(keyword): keyword.score for keyword in self.baka_series.weighed_keywords.all()}
        self.assertDictEqual(shingeki_keywords, baka_series_keywords)

    def test_store_correct_description(self):
        self.assertEqual(shingeki_description, self.baka_series.description)

    def test_store_correct_status(self):
        self.assertEqual(shingeki_status, self.baka_series.status)

    def test_store_correct_authors(self):
        baka_series_authors = {str(author) for author in self.baka_series.authors.all()}
        self.assertSetEqual(shingeki_authors, baka_series_authors)

    def test_store_correct_artists(self):
        baka_series_artists = {str(artist) for artist in self.baka_series.artists.all()}
        self.assertSetEqual(shingeki_artists, baka_series_artists)

    def test_store_correct_year(self):
        self.assertEqual(shingeki_year, self.baka_series.year)

    def test_store_correct_original_publisher(self):
        self.assertEqual(shingeki_original_publisher, self.baka_series.original_publisher)

    def test_store_correct_english_publisher(self):
        self.assertEqual(shingeki_english_publisher, self.baka_series.english_publisher)


class LazyIdUpgradeTests(TestCase):
    def fetch(self, manga, final_url=None):
        retriever = ShingekiMockBakaRetriever(final_url=final_url)
        baka_series = ExternalMangaFetcher(
            item=manga,
            sources=[BakaScraperSource(retriever)],
            image_retriever_class=MockImageRetriever,
        ).fetch()
        return baka_series, retriever

    def test_numeric_id_redirected_to_code_is_upgraded(self):
        manga = MockManga(baka_id=MOCK_BAKA_ID)
        baka_series, retriever = self.fetch(manga, final_url=MOCK_REDIRECT_URL)
        self.assertEqual([f"https://www.mangaupdates.com/series.html?id={MOCK_BAKA_ID}"], retriever.requested_urls)
        self.assertEqual(MOCK_BAKA_CODE, manga.baka_id)
        self.assertEqual(MOCK_BAKA_CODE, baka_series.baka_id)

    def test_numeric_id_without_redirect_is_kept(self):
        manga = MockManga(baka_id=MOCK_BAKA_ID)
        baka_series, _retriever = self.fetch(manga)
        self.assertEqual(MOCK_BAKA_ID, manga.baka_id)
        self.assertEqual(MOCK_BAKA_ID, baka_series.baka_id)

    def test_code_is_fetched_directly(self):
        manga = MockManga(baka_id=MOCK_BAKA_CODE)
        baka_series, retriever = self.fetch(manga, final_url=MOCK_REDIRECT_URL)
        self.assertEqual([f"https://www.mangaupdates.com/series/{MOCK_BAKA_CODE}"], retriever.requested_urls)
        self.assertEqual(MOCK_BAKA_CODE, manga.baka_id)
        self.assertEqual(MOCK_BAKA_CODE, baka_series.baka_id)


class MoreBakaParserTests(TestCase):
    def setUp(self):
        self.baka_series = ExternalMangaFetcher(
            item=MockManga(),
            sources=[BakaScraperSource(PrincessMockBakaRetriever())],
            image_retriever_class=MockImageRetriever,
        ).fetch()

    def test_store_correct_authors(self):
        baka_series_authors = {str(author) for author in self.baka_series.authors.all()}
        self.assertSetEqual(princess_authors, baka_series_authors)

    def test_store_correct_artists(self):
        baka_series_artists = {str(artist) for artist in self.baka_series.artists.all()}
        self.assertSetEqual(princess_artists, baka_series_artists)

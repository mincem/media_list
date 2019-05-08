from unittest import mock

from django.core.files.base import File
from django.test import TestCase

from ..utils import BakaParser

MOCK_BAKA_ID = 1234567

FMP_SIGMA_BAKA_ID = 913

shingeki_authors = {"ISAYAMA Hajime"}
shingeki_artists = {"ISAYAMA Hajime"}
shingeki_title = "Shingeki no Kyojin"
shingeki_year = 2009
shingeki_genres = {"Action", "Drama", "Fantasy", "Horror", "Mature", "Mystery", "Shounen", "Supernatural", "Tragedy"}
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


class ShingekiMockBakaRetriever:
    @staticmethod
    def get(_baka_id):
        with open("./media_list/samples/sample_baka.html", "rb") as html_file:
            return html_file.read()


class PrincessMockBakaRetriever:
    @staticmethod
    def get(_baka_id):
        with open("./media_list/samples/sample_baka_2.html", "rb") as html_file:
            return html_file.read()


class MockImageRetriever:
    @staticmethod
    def get(_image_url):
        return {
            "name": 'FileMock',
            "content": mock.MagicMock(spec=File, name='FileMock'),
        }


class BakaParserTests(TestCase):
    def setUp(self):
        self.baka_series = BakaParser(
            baka_id=MOCK_BAKA_ID,
            baka_retriever=ShingekiMockBakaRetriever(),
            image_retriever=MockImageRetriever(),
        ).perform()

    # def test_pending(self):
    #     parser = BakaParser(FMP_SIGMA_BAKA_ID, MockBakaRetriever())
    #     print(parser.display_parsed_data())  # Full Metal Panic Sigma (check sigma char)
    #     self.assertTrue(False)

    def test_store_correct_baka_id(self):
        self.assertEquals(MOCK_BAKA_ID, self.baka_series.baka_id)

    def test_store_correct_title(self):
        self.assertEquals(shingeki_title, self.baka_series.title)

    def test_store_correct_genres(self):
        baka_series_genres = {str(genre) for genre in self.baka_series.genres.all()}
        self.assertSetEqual(shingeki_genres, baka_series_genres)

    def test_store_correct_description(self):
        self.assertEquals(shingeki_description, self.baka_series.description)

    def test_store_correct_status(self):
        self.assertEquals(shingeki_status, self.baka_series.status)

    def test_store_correct_authors(self):
        baka_series_authors = {str(author) for author in self.baka_series.authors.all()}
        self.assertSetEqual(shingeki_authors, baka_series_authors)

    def test_store_correct_artists(self):
        baka_series_artists = {str(artist) for artist in self.baka_series.artists.all()}
        self.assertSetEqual(shingeki_artists, baka_series_artists)

    def test_store_correct_year(self):
        self.assertEquals(shingeki_year, self.baka_series.year)

    def test_store_correct_original_publisher(self):
        self.assertEquals(shingeki_original_publisher, self.baka_series.original_publisher)

    def test_store_correct_english_publisher(self):
        self.assertEquals(shingeki_english_publisher, self.baka_series.english_publisher)


class MoreBakaParserTests(TestCase):
    def setUp(self):
        self.baka_series = BakaParser(
            baka_id=MOCK_BAKA_ID,
            baka_retriever=PrincessMockBakaRetriever(),
            image_retriever=MockImageRetriever(),
        ).perform()

    def test_store_correct_authors(self):
        baka_series_authors = {str(author) for author in self.baka_series.authors.all()}
        self.assertSetEqual(princess_authors, baka_series_authors)

    def test_store_correct_artists(self):
        baka_series_artists = {str(artist) for artist in self.baka_series.artists.all()}
        self.assertSetEqual(princess_artists, baka_series_artists)

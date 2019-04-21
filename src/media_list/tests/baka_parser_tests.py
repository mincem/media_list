import os

from django.core.files.base import ContentFile
from django.templatetags.static import static
from django.test import TestCase

from ..utils import BakaParser

MOCK_BAKA_ID = 1234567

FMP_SIGMA_BAKA_ID = 913

shingeki_author = "ISAYAMA Hajime"
shingeki_artist = "ISAYAMA Hajime"
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


class MockBakaRetriever:
    @staticmethod
    def get(_baka_id):
        with open("./media_list/samples/sample_baka.html", "rb") as html_file:
            return html_file.read()


class MockImageRetriever:
    @staticmethod
    def get(_image_url):
        static_url = "media_list/images/shingeki_no_kyojin.png"
        with open("./media_list" + static(static_url), "rb") as image:
            return {
                "name": os.path.basename(static_url),
                "content": ContentFile(image.read()),
            }


class BakaParserTests(TestCase):
    def setUp(self):
        self.baka_series = BakaParser(
            baka_id=MOCK_BAKA_ID,
            baka_retriever=MockBakaRetriever(),
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

    def test_store_correct_author(self):
        self.assertEquals(shingeki_author, str(self.baka_series.author))

    def test_store_correct_artist(self):
        self.assertEquals(shingeki_artist, str(self.baka_series.artist))

    def test_store_correct_year(self):
        self.assertEquals(shingeki_year, self.baka_series.year)

    def test_store_correct_original_publisher(self):
        self.assertEquals(shingeki_original_publisher, self.baka_series.original_publisher)

    def test_store_correct_english_publisher(self):
        self.assertEquals(shingeki_english_publisher, self.baka_series.english_publisher)

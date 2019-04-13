from django.test import TestCase

from ..utils import BakaParser

MOCK_BAKA_ID = 1234567

FMP_SIGMA_BAKA_ID = 913

shingeki_author = "ISAYAMA Hajime"
shingeki_artist = "ISAYAMA Hajime"
shingeki_year = 2009
shingeki_genres = {"Action", "Drama", "Fantasy", "Horror", "Mature", "Mystery", "Shounen", "Supernatural", "Tragedy"}
shingeki_original_publisher = "Kodansha"
shingeki_english_publisher = "Kodansha Comics (26 Volumes - Ongoing)"


class MockBakaRetriever:
    @staticmethod
    def get(_baka_id):
        with open("./media_list/samples/sample_baka.html", "rb") as html_file:
            return html_file.read()


class BakaParserTests(TestCase):
    # def test_pending(self):
    #     parser = BakaParser(FMP_SIGMA_BAKA_ID, MockBakaRetriever())
    #     print(parser.display_parsed_data())  # Full Metal Panic Sigma (check sigma char)
    #     self.assertTrue(False)

    def test_store_correct_baka_id(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        self.assertEquals(MOCK_BAKA_ID, baka_series.baka_id)

    def test_store_correct_author(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        self.assertEquals(shingeki_author, str(baka_series.author))

    def test_store_correct_artist(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        self.assertEquals(shingeki_artist, str(baka_series.artist))

    def test_store_correct_genres(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        baka_series_genres = {str(genre) for genre in baka_series.genres.all()}
        self.assertSetEqual(shingeki_genres, baka_series_genres)

    def test_store_correct_original_publisher(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        self.assertEquals(shingeki_original_publisher, baka_series.original_publisher)

    def test_store_correct_english_publisher(self):
        baka_series = BakaParser(MOCK_BAKA_ID, MockBakaRetriever()).baka_series()
        self.assertEquals(shingeki_english_publisher, baka_series.english_publisher)

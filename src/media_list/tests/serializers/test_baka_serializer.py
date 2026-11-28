from django.test import TestCase

from ...serializers.baka_serializer import BakaSerializer


class MockManga:
    def __init__(self, baka_id=None):
        self.baka_id = baka_id


class TestBakaSerializer(TestCase):
    def test_numeric_id_url(self):
        expected = "https://www.mangaupdates.com/series.html?id=12345"
        url = BakaSerializer.numeric_id_url(12345)
        self.assertEqual(expected, url)

    def test_alphanumeric_code_url(self):
        expected = "https://www.mangaupdates.com/series/a1b2c3d4"
        url = BakaSerializer.alphanumeric_code_url("a1b2c3d4")
        self.assertEqual(expected, url)

    def test_url_with_numeric_id(self):
        expected = "https://www.mangaupdates.com/series.html?id=12345"
        for baka_id in ("12345", 12345):
            with self.subTest(baka_id=baka_id):
                self.assertEqual(expected, BakaSerializer().url(MockManga(baka_id=baka_id)))

    def test_url_with_alphanumeric_code(self):
        expected = "https://www.mangaupdates.com/series/a1b2c3d4"
        url = BakaSerializer().url(MockManga(baka_id="a1b2c3d4"))
        self.assertEqual(expected, url)

    def test_url_with_no_id(self):
        for baka_id in (None, ""):
            with self.subTest(baka_id=baka_id):
                with self.assertRaises(Exception) as content_manager:
                    BakaSerializer().url(MockManga(baka_id=baka_id))
                self.assertEqual("Missing external item ID", str(content_manager.exception))

    def test_code_from_url(self):
        data = {
            "https://www.mangaupdates.com/series/5b8ska1/tangled-hyungjakga": "5b8ska1",
            "https://www.mangaupdates.com/series/5b8ska1": "5b8ska1",
            "https://www.mangaupdates.com/series.html?id=150000": None,
        }
        for url, expected in data.items():
            with self.subTest(url=url):
                self.assertEqual(expected, BakaSerializer.code_from_url(url))

    def test_upgraded_id_from_redirected_numeric_id(self):
        final_url = "https://www.mangaupdates.com/series/5b8ska1/tangled-hyungjakga"
        new_id = BakaSerializer().upgraded_id("150000", final_url)
        self.assertEqual("5b8ska1", new_id)

    def test_upgraded_id_without_redirect(self):
        new_id = BakaSerializer().upgraded_id("150000", "https://www.mangaupdates.com/series.html?id=150000")
        self.assertEqual("150000", new_id)

    def test_upgraded_id_keeps_existing_code(self):
        new_id = BakaSerializer().upgraded_id("a1b2c3d4", "https://www.mangaupdates.com/series/zzzzzzz/other")
        self.assertEqual("a1b2c3d4", new_id)


class TestBakaCodeFromApiId(TestCase):
    def test_author_id_from_sample(self):
        self.assertEqual("py2nfr7", BakaSerializer.code_from_api_id(56479861123))

    def test_inverse_of_api_series_id(self):
        for code in ("aqw5kar", "dn77cs0", "jacyd12", "1", "z"):
            with self.subTest(code=code):
                self.assertEqual(code, BakaSerializer.code_from_api_id(BakaSerializer.api_series_id(code)))

    def test_zero(self):
        self.assertEqual("0", BakaSerializer.code_from_api_id(0))

    def test_negative_is_rejected(self):
        with self.assertRaises(ValueError):
            BakaSerializer.code_from_api_id(-1)

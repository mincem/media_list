from django.test import TestCase

from ...serializers.baka_serializer import BakaSerializer


class MockManga:
    def __init__(self, baka_id=None, baka_code=None):
        self.baka_id = baka_id
        self.baka_code = baka_code


class TestBakaSerializer(TestCase):
    def test_numeric_id_url(self):
        expected = "https://www.mangaupdates.com/series.html?id=12345"
        url = BakaSerializer.numeric_id_url(12345)
        self.assertEqual(expected, url)

    def test_alphanumeric_code_url(self):
        expected = "https://www.mangaupdates.com/series/a1b2c3d4"
        url = BakaSerializer.alphanumeric_code_url("a1b2c3d4")
        self.assertEqual(expected, url)

    def test_url_with_baka_id(self):
        expected = "https://www.mangaupdates.com/series.html?id=12345"
        url = BakaSerializer().url(MockManga(baka_id=12345))
        self.assertEqual(expected, url)

    def test_url_with_baka_code(self):
        expected = "https://www.mangaupdates.com/series/a1b2c3d4"
        url = BakaSerializer().url(MockManga(baka_code="a1b2c3d4"))
        self.assertEqual(expected, url)

    def test_url_with_both_ids(self):
        expected = "https://www.mangaupdates.com/series/a1b2c3d4"
        url = BakaSerializer().url(MockManga(baka_id=12345, baka_code="a1b2c3d4"))
        self.assertEqual(expected, url)

    def test_url_with_no_ids(self):
        with self.assertRaises(Exception) as content_manager:
            BakaSerializer().url(MockManga())
        self.assertEqual("Missing external item ID", str(content_manager.exception))

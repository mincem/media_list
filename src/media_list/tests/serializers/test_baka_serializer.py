from django.test import TestCase

from ...serializers.baka_serializer import BakaSerializer


class TestBakaSerializer(TestCase):
    def test_numeric_id_url(self):
        self.assertEqual(
            "https://www.mangaupdates.com/series.html?id=12345",
            BakaSerializer.numeric_id_url("12345")
        )

    def test_alphanumeric_code_url(self):
        self.assertEqual(
            "https://www.mangaupdates.com/series/a1b2c3d4",
            BakaSerializer.alphanumeric_code_url("a1b2c3d4")
        )

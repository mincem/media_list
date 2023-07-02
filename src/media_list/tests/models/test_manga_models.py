from django.test import TestCase

from ...models import MangaSeries

NUMERIC_ID = 12345
ALPHANUMERIC_ID = "a1b2c3d4"


class MangaSeriesTests(TestCase):
    def setUp(self):
        self.manga_series = MangaSeries(
            interest=50,
        )
        self.manga_series.save()

    def test_external_id_with_numeric_id(self):
        self.assertEqual(None, self.manga_series.external_id)
        self.manga_series.external_id = NUMERIC_ID
        self.manga_series.save()
        self.assertEqual(NUMERIC_ID, self.manga_series.external_id)
        self.assertEqual(NUMERIC_ID, self.manga_series.baka_id)

    def test_external_id_with_alphanumeric_id(self):
        self.assertEqual(None, self.manga_series.external_id)
        self.manga_series.external_id = ALPHANUMERIC_ID
        self.manga_series.save()
        self.assertEqual(ALPHANUMERIC_ID, self.manga_series.external_id)
        self.assertEqual(ALPHANUMERIC_ID, self.manga_series.baka_code)

    def test_display_volumes(self):
        data = (dict.values() for dict in (
            {"volumes": 1, "has_omnibus": False, "is_completed": True, "expected": "One-shot"},
            {"volumes": 1, "has_omnibus": False, "is_completed": False, "expected": "1+ volumes"},
            {"volumes": 25, "has_omnibus": False, "is_completed": True, "expected": "25 volumes"},
            {"volumes": 25, "has_omnibus": False, "is_completed": False, "expected": "25+ volumes"},
            {"volumes": 1, "has_omnibus": True, "is_completed": True, "expected": "Omnibus One-shot"},
            {"volumes": 1, "has_omnibus": True, "is_completed": False, "expected": "1+ omnibus"},
            {"volumes": 25, "has_omnibus": True, "is_completed": True, "expected": "25 omnibus"},
            {"volumes": 25, "has_omnibus": True, "is_completed": False, "expected": "25+ omnibus"},
        ))

        for volumes, has_omnibus, is_completed, expected in data:
            with self.subTest(f"for {expected}"):
                self.manga_series.volumes = volumes
                self.manga_series.has_omnibus = has_omnibus
                self.manga_series.is_completed = is_completed
                self.manga_series.save()
                self.assertEqual(expected, self.manga_series.display_volumes())

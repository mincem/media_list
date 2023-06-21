from django.test import TestCase

from ..models import MangaSeries


class MangaSeriesFormsTests(TestCase):
    def setUp(self):
        self.title = "Title"
        self.alternate_title = "Alt"

    def test_item_fields_are_swapped(self):
        ms = MangaSeries.objects.create(
            title=self.title,
            alternate_title=self.alternate_title,
            interest=2,
        )
        ms.title, ms.alternate_title = ms.alternate_title, ms.title

        self.assertEqual(self.title, ms.alternate_title)
        self.assertEqual(self.alternate_title, ms.title)

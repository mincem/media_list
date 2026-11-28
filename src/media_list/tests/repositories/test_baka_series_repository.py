from django.test import TestCase

from ...models import MangaPerson
from ...repositories import BakaSeriesRepository

WATASE_ID = "jacyd12"


def alice_19th_data(**overrides):
    """Alice 19th (dn77cs0) credits one person twice, spelling the name differently in each credit."""
    return {
        "baka_id": "dn77cs0",
        "title": "Alice 19th",
        "authors": [{"id": WATASE_ID, "name": "WATASE Yuu"}],
        "artists": [{"id": WATASE_ID, "name": "Watase Yuu"}],
        **overrides,
    }


class BakaSeriesRepositoryPeopleTests(TestCase):
    def test_one_person_for_differently_spelled_credits_with_same_id(self):
        baka_series = BakaSeriesRepository().create(**alice_19th_data())
        self.assertEqual(1, MangaPerson.objects.count())
        self.assertTrue(baka_series.has_single_author())

    def test_give_id_to_person_stored_before_ids(self):
        legacy_person = MangaPerson.objects.create(name="WATASE Yuu")
        baka_series = BakaSeriesRepository().create(**alice_19th_data())
        legacy_person.refresh_from_db()
        self.assertEqual(WATASE_ID, legacy_person.baka_author_id)
        self.assertEqual(legacy_person, baka_series.single_author())

    def test_namesakes_with_different_ids_are_different_people(self):
        baka_series = BakaSeriesRepository().create(**alice_19th_data(
            artists=[{"id": "py2nfr7", "name": "WATASE Yuu"}],
        ))
        self.assertEqual(2, MangaPerson.objects.filter(name="WATASE Yuu").count())
        self.assertFalse(baka_series.has_single_author())

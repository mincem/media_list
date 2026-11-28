from django.test import TestCase

from ...models import MangaPerson, VideoPerson


class PersonFromCreditTestsMixin:
    """Tests PersonManager.from_credit, run once per Person subclass."""
    model = None
    first_id = None
    second_id = None

    def create(self, external_id=None, name="Some Name"):
        return self.model.objects.create(**{self.model.external_id_field: external_id, "name": name})

    def external_id_of(self, person):
        return getattr(person, self.model.external_id_field)

    def test_reuse_person_with_same_id(self):
        person = self.create(external_id=self.first_id)
        self.assertEqual(person, self.model.objects.from_credit(self.first_id, "Some Name"))
        self.assertEqual(1, self.model.objects.count())

    def test_keep_stored_name_when_spelling_differs(self):
        person = self.create(external_id=self.first_id, name="WATASE Yuu")
        self.assertEqual(person, self.model.objects.from_credit(self.first_id, "Watase Yuu"))
        person.refresh_from_db()
        self.assertEqual("WATASE Yuu", person.name)

    def test_give_id_to_single_namesake_without_id(self):
        legacy_person = self.create()
        self.assertEqual(legacy_person, self.model.objects.from_credit(self.first_id, "Some Name"))
        legacy_person.refresh_from_db()
        self.assertEqual(self.first_id, self.external_id_of(legacy_person))
        self.assertEqual(1, self.model.objects.count())

    def test_dont_adopt_namesake_with_other_id(self):
        self.create(external_id=self.first_id)
        person = self.model.objects.from_credit(self.second_id, "Some Name")
        self.assertEqual(self.second_id, self.external_id_of(person))
        self.assertEqual(2, self.model.objects.filter(name="Some Name").count())

    def test_create_person_when_several_namesakes_have_no_id(self):
        first, second = self.create(), self.create()
        person = self.model.objects.from_credit(self.first_id, "Some Name")
        self.assertNotIn(person, (first, second))
        self.assertEqual(self.first_id, self.external_id_of(person))

    def test_credit_without_id_reuses_namesake_without_id(self):
        person = self.create()
        self.assertEqual(person, self.model.objects.from_credit(None, "Some Name"))
        self.assertEqual(1, self.model.objects.count())

    def test_credit_without_id_creates_person_when_no_namesake(self):
        self.create(external_id=self.first_id)
        person = self.model.objects.from_credit(None, "Some Name")
        self.assertIsNone(self.external_id_of(person))
        self.assertEqual(2, self.model.objects.count())


class MangaPersonFromCreditTests(PersonFromCreditTestsMixin, TestCase):
    model = MangaPerson
    first_id = "jacyd12"
    second_id = "py2nfr7"


class VideoPersonFromCreditTests(PersonFromCreditTestsMixin, TestCase):
    model = VideoPerson
    first_id = 1
    second_id = 2

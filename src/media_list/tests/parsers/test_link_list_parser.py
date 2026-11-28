import json

from django.test import TestCase
from django.urls import reverse

from ...models import MangaSeries
from ...parsers import link_list_parser


class ParseEntryTests(TestCase):
    def assert_parsed(self, text, title, volumes):
        entry = link_list_parser.parse_entry(text=text, url="https://example.com/x")
        self.assertEqual(entry["title"], title)
        self.assertEqual(entry["volumes"], volumes)
        self.assertEqual(entry["full_text"], text)
        self.assertEqual(entry["link"], "https://example.com/x")

    def test_title_and_volumes(self):
        self.assert_parsed("Berserk v41 (Digital)", "Berserk", 41)
        self.assert_parsed("One Piece v1-v105 (Complete)", "One Piece", 105)
        self.assert_parsed("Monster 18 [Scans]", "Monster", 18)

    def test_title_and_bracket(self):
        self.assert_parsed("Dorohedoro (Complete)", "Dorohedoro", 0)
        self.assert_parsed("Dorohedoro(Complete)", "Dorohedoro", 0)

    def test_title_only(self):
        self.assert_parsed("Berserk", "Berserk", 0)
        self.assert_parsed("Vinland Saga - Read Manga Online", "Vinland Saga - Read Manga Online", 0)

    def test_title_starting_with_punctuation(self):
        self.assert_parsed(".hack//Legend of the Twilight 3", ".hack//Legend of the Twilight", 3)
        self.assert_parsed('"Oshi no Ko" 3', '"Oshi no Ko"', 3)

    def test_surrounding_whitespace(self):
        self.assert_parsed("  Berserk 41  ", "Berserk", 41)

    def test_blank_text(self):
        MangaSeries.objects.create(title="Berserk", interest=50)
        entry = link_list_parser.parse_entry(text="   ", url="https://example.com/x")
        self.assertEqual(entry["title"], "")
        self.assertEqual(entry["volumes"], 0)
        self.assertEqual(list(entry["matches"]), [])


LINKS = [
    {"text": "Berserk v41 (Digital)", "url": "https://example.com/berserk"},
    {"text": "Vinland Saga", "url": "https://example.com/vinland"},
    {"text": "", "url": "https://example.com/blank"},
    {"text": "Monster 18 [Scans]", "url": "https://example.com/monster(manga)"},
]


class ProcessLinksTests(TestCase):
    def setUp(self):
        self.berserk = MangaSeries.objects.create(title="Berserk", interest=50)

    def test_every_link_gives_an_entry(self):
        entries = link_list_parser.process_links(LINKS)
        self.assertEqual(
            [(entry["title"], entry["volumes"], entry["link"]) for entry in entries],
            [
                ("Berserk", 41, "https://example.com/berserk"),
                ("Vinland Saga", 0, "https://example.com/vinland"),
                ("", 0, "https://example.com/blank"),
                ("Monster", 18, "https://example.com/monster(manga)"),
            ]
        )
        self.assertEqual([match["id"] for match in entries[0]["matches"]], [self.berserk.id])
        self.assertEqual(entries[2]["matches"], [])


class BatchMangaImporterViewTests(TestCase):
    def post(self, body):
        return self.client.post(reverse("batch"), body, content_type="application/json")

    def test_get_sets_csrf_cookie(self):
        response = self.client.get(reverse("batch"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_returns_an_item_per_link(self):
        response = self.post(json.dumps({"links": LINKS}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["link"] for item in response.json()["items"]], [link["url"] for link in LINKS])

    def test_rejects_invalid_json(self):
        self.assertEqual(self.post("not json").status_code, 400)

    def test_rejects_invalid_links(self):
        for body in [{}, {"links": []}, {"links": [{"text": "Berserk"}]}, {"links": [{"text": "x", "url": "nope"}]}]:
            with self.subTest(body=body):
                self.assertEqual(self.post(json.dumps(body)).status_code, 400)

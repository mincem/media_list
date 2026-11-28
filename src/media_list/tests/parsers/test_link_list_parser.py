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


class ProcessMarkdownTests(TestCase):
    markdown = "\n".join([
        "- [Berserk v41 (Digital)](https://example.com/berserk)",
        "- [Vinland Saga](https://example.com/vinland)",
        "- [ ](https://example.com/blank)",
        "- [Monster 18 [Scans]](https://example.com/monster)",
    ])

    def setUp(self):
        self.berserk = MangaSeries.objects.create(title="Berserk", interest=50)

    def test_every_link_gives_an_entry(self):
        entries = link_list_parser.process_markdown(self.markdown)
        self.assertEqual(
            [(entry["title"], entry["volumes"], entry["link"]) for entry in entries],
            [
                ("Berserk", 41, "https://example.com/berserk"),
                ("Vinland Saga", 0, "https://example.com/vinland"),
                ("", 0, "https://example.com/blank"),
                ("Monster", 18, "https://example.com/monster"),
            ]
        )
        self.assertEqual([match["id"] for match in entries[0]["matches"]], [self.berserk.id])
        self.assertEqual(entries[2]["matches"], [])

    def test_view_returns_all_entries(self):
        response = self.client.post(reverse("batch"), {"links": self.markdown})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 4)

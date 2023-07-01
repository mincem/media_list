from django.test import TestCase

from ...id_finders import BakaIDFinder, BakaUrlException

SERIES_TITLE = "Some Title"

NUMERIC_ID = 12345
ALPHANUMERIC_ID = "a1b2c3d4"

NUMERIC_ID_URL = f"https://www.mangaupdates.com/series.html?id={NUMERIC_ID}"
ALPHANUMERIC_ID_URL = f"https://www.mangaupdates.com/series/{ALPHANUMERIC_ID}"
ALPHANUMERIC_ID_URL_WITH_SLUG = f"https://www.mangaupdates.com/series/{ALPHANUMERIC_ID}/blah-blah-blah"


class TestBakaIDFinder(TestCase):
    def test_get_id_from_numeric_url(self):
        link_fetcher = MockLinkFetcher(NUMERIC_ID_URL)
        finder = BakaIDFinder(SERIES_TITLE, link_fetcher)
        self.assertEqual(NUMERIC_ID, finder.get_id())

    def test_get_id_from_alphanumeric_url(self):
        link_fetcher = MockLinkFetcher(ALPHANUMERIC_ID_URL)
        finder = BakaIDFinder(SERIES_TITLE, link_fetcher)
        self.assertEqual(ALPHANUMERIC_ID, finder.get_id())

    def test_get_id_from_alphanumeric_url_with_slug(self):
        link_fetcher = MockLinkFetcher(ALPHANUMERIC_ID_URL_WITH_SLUG)
        finder = BakaIDFinder(SERIES_TITLE, link_fetcher)
        self.assertEqual(ALPHANUMERIC_ID, finder.get_id())

    def test_get_id_from_different_host_url(self):
        wrong_url = "https://www.google.com/series/123"
        link_fetcher = MockLinkFetcher(wrong_url)
        with self.assertRaises(BakaUrlException) as content_manager:
            BakaIDFinder(SERIES_TITLE, link_fetcher).get_id()
        self.assertEqual(f"Cannot get Baka-ID from URL: {wrong_url}", str(content_manager.exception))

    def test_get_id_from_url_with_no_id(self):
        wrong_url = "https://www.mangaupdates.com/series.html"
        link_fetcher = MockLinkFetcher(wrong_url)
        with self.assertRaises(BakaUrlException) as content_manager:
            BakaIDFinder(SERIES_TITLE, link_fetcher).get_id()
        self.assertEqual(f"Cannot get Baka-ID from URL: {wrong_url}", str(content_manager.exception))

class MockLinkFetcher:
    def __init__(self, url):
        self.url = url

    def fetch(self, _series_title):
        return self.url

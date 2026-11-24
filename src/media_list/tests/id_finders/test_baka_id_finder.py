import requests
from django.test import TestCase

from ...id_finders import BakaIDFinder, BakaSearchException, BakaUrlException, LinkFetcher

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


def search_result(hit_title, code):
    return {
        "hit_title": hit_title,
        "record": {"series_id": int(code, 36), "url": f"https://www.mangaupdates.com/series/{code}/slug"},
    }


class MockSearchRetriever:
    def __init__(self, results=None, error=None):
        self.results = results or []
        self.error = error
        self.searches = []

    def search(self, series_title):
        self.searches.append(series_title)
        if self.error:
            raise self.error
        return self.results


class TestLinkFetcher(TestCase):
    def test_prefers_exact_hit_title_match(self):
        retriever = MockSearchRetriever([
            search_result("Shingeki no Kyojin dj - Something", "aaa111"),
            search_result("shingeki  no KYOJIN", "bbb222"),
        ])
        url = LinkFetcher(retriever).fetch("Shingeki no Kyojin")
        self.assertEqual("https://www.mangaupdates.com/series/bbb222/slug", url)
        self.assertEqual(["Shingeki no Kyojin"], retriever.searches)

    def test_falls_back_to_first_result(self):
        retriever = MockSearchRetriever([
            search_result("Something Else", "aaa111"),
            search_result("Another Thing", "bbb222"),
        ])
        url = LinkFetcher(retriever).fetch("Some Title")
        self.assertEqual("https://www.mangaupdates.com/series/aaa111/slug", url)

    def test_no_results_raises(self):
        with self.assertRaises(BakaSearchException) as content_manager:
            LinkFetcher(MockSearchRetriever([])).fetch("Some Title")
        self.assertEqual('Cannot find Mangaupdates page for series "Some Title"', str(content_manager.exception))

    def test_http_error_propagates(self):
        retriever = MockSearchRetriever(error=requests.HTTPError("504"))
        with self.assertRaises(requests.HTTPError):
            LinkFetcher(retriever).fetch("Some Title")

    def test_finder_returns_id_from_search(self):
        retriever = MockSearchRetriever([search_result("Some Title", "aqw5kar")])
        self.assertEqual("aqw5kar", BakaIDFinder(SERIES_TITLE, LinkFetcher(retriever)).get_id())

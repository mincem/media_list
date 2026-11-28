from types import SimpleNamespace
from unittest import TestCase as SimpleTestCase

import requests

from ..id_finders.test_baka_id_finder import MockSearchRetriever
from ...data_fetchers.baka_id_resolver import BakaIDResolutionError, BakaIDResolver

OLD_ID = "2"
OLD_URL = f"https://www.mangaupdates.com/series.html?id={OLD_ID}"
CODE = "a1b2c3d"
OTHER_CODE = "z9y8x7w"
TITLE = "Hanazakari no Kimitachi e"


class MockRedirectReader:
    """Maps each URL to where it redirects (absent: not a redirect). An exception value is raised instead."""

    def __init__(self, locations=None):
        self.locations = locations or {}
        self.requested_urls = []

    def location(self, url):
        self.requested_urls.append(url)
        location = self.locations.get(url)
        if isinstance(location, Exception):
            raise location
        return location


def search_result(title, code, year=None, hit_title=None):
    return {
        "hit_title": hit_title or title,
        "record": {
            "series_id": int(code, 36),
            "title": title,
            "url": f"https://www.mangaupdates.com/series/{code}/slug",
            "year": year,
        },
    }


def manga(title=TITLE, info_title=None, info_year=None):
    """A manga with the old ID; with info if info_title is given."""
    baka_info = SimpleNamespace(title=info_title, year=info_year) if info_title else None
    return SimpleNamespace(baka_id=OLD_ID, title=title, baka_info=baka_info)


class RedirectTests(SimpleTestCase):
    def resolve(self, locations, results=None):
        reader = MockRedirectReader(locations)
        retriever = MockSearchRetriever(results)
        return BakaIDResolver(reader, retriever).resolve(manga()), reader, retriever

    def test_redirect_to_code_url(self):
        code, reader, retriever = self.resolve({OLD_URL: f"https://www.mangaupdates.com/series/{CODE}/slug"})
        self.assertEqual(CODE, code)
        self.assertEqual([OLD_URL], reader.requested_urls)
        self.assertEqual([], retriever.searches)

    def test_relative_redirect(self):
        code, _reader, _retriever = self.resolve({OLD_URL: f"/series/{CODE}/slug"})
        self.assertEqual(CODE, code)

    def test_redirect_with_several_hops(self):
        middle_url = "https://www.mangaupdates.com/series.html?id=2&step=1"
        code, reader, _retriever = self.resolve({
            OLD_URL: middle_url,
            middle_url: f"https://www.mangaupdates.com/series/{CODE}",
        })
        self.assertEqual(CODE, code)
        self.assertEqual([OLD_URL, middle_url], reader.requested_urls)

    def test_too_many_hops_falls_back_to_search(self):
        loop = {OLD_URL: OLD_URL}
        code, reader, retriever = self.resolve(loop, results=[search_result(TITLE, OTHER_CODE)])
        self.assertEqual(OTHER_CODE, code)
        self.assertEqual(3, len(reader.requested_urls))
        self.assertEqual([TITLE], retriever.searches)

    def test_no_redirect_falls_back_to_search(self):
        code, _reader, retriever = self.resolve({}, results=[search_result(TITLE, OTHER_CODE)])
        self.assertEqual(OTHER_CODE, code)
        self.assertEqual([TITLE], retriever.searches)

    def test_failed_redirect_request_falls_back_to_search(self):
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            code, _reader, _retriever = self.resolve(
                {OLD_URL: requests.HTTPError("429 Too Many Requests")}, results=[search_result(TITLE, OTHER_CODE)],
            )
        self.assertEqual(OTHER_CODE, code)


class InfoSearchTests(SimpleTestCase):
    """Manga with info: only an exact match of the info's main title (and year) is accepted."""

    def resolve(self, results, info_title="Hana-Kimi", info_year=1996):
        resolver = BakaIDResolver(MockRedirectReader(), MockSearchRetriever(results))
        return resolver.resolve(manga(info_title=info_title, info_year=info_year))

    def test_searches_the_info_title_not_the_manga_title(self):
        retriever = MockSearchRetriever([search_result("Hana-Kimi", CODE)])
        BakaIDResolver(MockRedirectReader(), retriever).resolve(manga(info_title="Hana-Kimi"))
        self.assertEqual(["Hana-Kimi"], retriever.searches)

    def test_exact_main_title_match(self):
        code = self.resolve([
            search_result("Hana-Kimi dj", OTHER_CODE),
            search_result("hana-kimi", CODE, year="1996"),
        ])
        self.assertEqual(CODE, code)

    def test_match_on_alternate_hit_title_only_is_rejected(self):
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            with self.assertRaises(BakaIDResolutionError):
                self.resolve([search_result("Hanazakari no Kimitachi e", CODE, hit_title="Hana-Kimi")])

    def test_year_picks_between_same_titles(self):
        code = self.resolve([
            search_result("Hana-Kimi", OTHER_CODE, year="2007"),
            search_result("Hana-Kimi", CODE, year="1996"),
        ])
        self.assertEqual(CODE, code)

    def test_year_mismatch_is_rejected(self):
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            with self.assertRaises(BakaIDResolutionError):
                self.resolve([search_result("Hana-Kimi", CODE, year="2007")])

    def test_ambiguous_match_is_rejected(self):
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            with self.assertRaises(BakaIDResolutionError):
                self.resolve([search_result("Hana-Kimi", CODE), search_result("Hana-Kimi", OTHER_CODE)])

    def test_search_failure(self):
        resolver = BakaIDResolver(MockRedirectReader(), MockSearchRetriever(error=requests.ConnectionError("down")))
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            with self.assertRaises(BakaIDResolutionError) as context_manager:
                resolver.resolve(manga(info_title="Hana-Kimi"))
        self.assertEqual(
            f"Cannot find the current Mangaupdates code for the old ID {OLD_ID}", str(context_manager.exception),
        )


class TitleSearchTests(SimpleTestCase):
    """Manga without info: found like a manga with no ID, with the manga's own title."""

    def resolve(self, results):
        retriever = MockSearchRetriever(results)
        return BakaIDResolver(MockRedirectReader(), retriever).resolve(manga()), retriever

    def test_exact_hit_title_match(self):
        code, retriever = self.resolve([
            search_result("Something Else", OTHER_CODE),
            search_result("Official Title", CODE, hit_title=TITLE),
        ])
        self.assertEqual(CODE, code)
        self.assertEqual([TITLE], retriever.searches)

    def test_first_result_without_exact_match(self):
        code, _retriever = self.resolve([search_result("Something Else", OTHER_CODE), search_result("Other", CODE)])
        self.assertEqual(OTHER_CODE, code)

    def test_no_results(self):
        with self.assertLogs("media_list.data_fetchers.baka_id_resolver", level="WARNING"):
            with self.assertRaises(BakaIDResolutionError):
                self.resolve([])

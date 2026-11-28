import io
import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import requests
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from ..data_fetchers.test_baka_sources import SHINGEKI_CODE, load_sample_json
from ..data_fetchers.test_refresh import CoverRetriever
from ...management.commands.convert_old_baka_ids import Command, match_verdict
from ...models import BakaSeries, MangaPerson, MangaSeries


class MockApiRetriever:
    """Serves the API sample for every code, or what `responses` gives for it: a value, an exception to raise, or a
    list of those to use in order."""
    requested_codes = []
    responses = {}

    def get(self, code):
        MockApiRetriever.requested_codes.append(code)
        response = MockApiRetriever.responses.get(code)
        if isinstance(response, list):
            response = response.pop(0)
        if isinstance(response, Exception):
            raise response
        return response if response is not None else load_sample_json()


class FailingCoverRetriever:
    def __init__(self, _image_url):
        pass

    def fetch(self):
        raise requests.ConnectionError("CDN down")


class ReviewTests(TestCase):
    """--review: one API request per old ID, then the user accepts (Enter), skips (s) or quits (q)."""

    def setUp(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        self.mapping_path = Path(folder) / "mapping.json"
        self.mapping_path.write_text(json.dumps({"47446": SHINGEKI_CODE, "2": "tsd1hyz"}), encoding="utf-8")
        MockApiRetriever.requested_codes = []
        MockApiRetriever.responses = {}
        CoverRetriever.fetched_urls = []

    def review(self, answers, *args, image_retriever_class=CoverRetriever):
        output = io.StringIO()
        with mock.patch.object(Command, "input_function", side_effect=answers), \
                mock.patch.object(Command, "api_retriever_class", MockApiRetriever), \
                mock.patch.object(Command, "image_retriever_class", image_retriever_class):
            call_command(
                "convert_old_baka_ids", "--mapping", str(self.mapping_path), "--review", *args,
                stdout=output, no_color=True,
            )
        return output.getvalue()

    @staticmethod
    def shingeki(baka_id="47446", with_info=True, title="Attack on Titan"):
        info = None
        if with_info:
            info = BakaSeries.objects.create(baka_id=baka_id, title="Shingeki no Kyojin", year=2009)
            info.authors.add(MangaPerson.objects.get_or_create(name="ISAYAMA Hajime")[0])
        return MangaSeries.objects.create(title=title, interest=50, baka_id=baka_id, baka_info=info)

    def test_accept_converts_manga_and_info_with_one_request(self):
        manga = self.shingeki()
        self.review([""])
        manga.refresh_from_db()
        manga.baka_info.refresh_from_db()
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)
        self.assertEqual(SHINGEKI_CODE, manga.baka_info.baka_id)
        self.assertEqual([SHINGEKI_CODE], MockApiRetriever.requested_codes)

    def test_shows_comparison_and_verdict(self):
        self.shingeki()
        output = self.review([""])
        self.assertIn(f"[1/1] 47446 -> {SHINGEKI_CODE}  https://www.mangaupdates.com/series/{SHINGEKI_CODE}", output)
        self.assertRegex(output, r"title +Shingeki no Kyojin +Shingeki no Kyojin")
        self.assertRegex(output, r"year +2009 +2009")
        self.assertIn("MATCH (title, year, author)", output)

    def test_manga_without_info_is_compared_by_its_own_title(self):
        self.shingeki(with_info=False, title="AoT")
        output = self.review([""])
        self.assertIn("manga (no info)", output)
        self.assertIn("PARTIAL (alternate title)", output)

    def test_skip_keeps_numeric_id(self):
        manga = self.shingeki()
        output = self.review(["s"])
        manga.refresh_from_db()
        self.assertEqual("47446", manga.baka_id)
        self.assertIn("0 accepted, 1 skipped", output)

    def test_quit_stops_before_the_next_id(self):
        first = MangaSeries.objects.create(title="Hana-Kimi", interest=50, baka_id="2")
        second = self.shingeki()
        output = self.review(["q"])
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual("2", first.baka_id)
        self.assertEqual("47446", second.baka_id)
        self.assertEqual(["tsd1hyz"], MockApiRetriever.requested_codes)
        self.assertIn("Stopped", output)

    def test_accepted_ids_are_kept_after_quitting(self):
        first = MangaSeries.objects.create(title="Hana-Kimi", interest=50, baka_id="2")
        second = self.shingeki()
        self.review(["", "q"])
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual("tsd1hyz", first.baka_id)
        self.assertEqual("47446", second.baka_id)

    def test_invalid_answer_asks_again(self):
        manga = self.shingeki()
        self.review(["yes", ""])
        manga.refresh_from_db()
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)

    def test_failed_request_is_retried_only_when_asked(self):
        manga = self.shingeki()
        MockApiRetriever.responses = {SHINGEKI_CODE: [requests.HTTPError("429"), load_sample_json()]}
        output = self.review(["r", ""])
        manga.refresh_from_db()
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)
        self.assertEqual([SHINGEKI_CODE, SHINGEKI_CODE], MockApiRetriever.requested_codes)
        self.assertIn("Cannot fetch", output)

    def test_failed_request_can_be_skipped(self):
        manga = self.shingeki()
        MockApiRetriever.responses = {SHINGEKI_CODE: requests.HTTPError("429")}
        self.review(["s"])
        manga.refresh_from_db()
        self.assertEqual("47446", manga.baka_id)

    def test_without_refresh_info_is_not_updated(self):
        manga = self.shingeki()
        self.review([""])
        manga.baka_info.refresh_from_db()
        self.assertEqual(0, manga.baka_info.genres.count())
        self.assertEqual([], CoverRetriever.fetched_urls)

    def test_refresh_stores_reviewed_data_in_place_without_another_request(self):
        manga = self.shingeki()
        old_info_pk = manga.baka_info_id
        output = self.review([""], "--refresh")
        manga.refresh_from_db()
        self.assertEqual(old_info_pk, manga.baka_info_id)
        self.assertEqual(1, BakaSeries.objects.count())
        self.assertEqual(220, manga.baka_info.keywords.count())
        self.assertTrue(manga.baka_info.image)
        self.assertEqual([SHINGEKI_CODE], MockApiRetriever.requested_codes)
        self.assertIn("Refreshed info", output)

    def test_refresh_merges_duplicate_infos_of_one_old_id(self):
        first, second = self.shingeki(), self.shingeki(title="Shingeki")
        duplicate_pk = second.baka_info_id
        self.review([""], "--refresh")
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.baka_info_id, second.baka_info_id)
        self.assertFalse(BakaSeries.objects.filter(pk=duplicate_pk).exists())
        self.assertEqual(1, len(CoverRetriever.fetched_urls))

    def test_refresh_gives_info_to_manga_without_it(self):
        manga = self.shingeki(with_info=False)
        self.review([""], "--refresh")
        manga.refresh_from_db()
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)
        self.assertEqual("Shingeki no Kyojin", manga.baka_info.title)

    def test_failed_refresh_keeps_converted_id(self):
        manga = self.shingeki()
        output = self.review([""], "--refresh", image_retriever_class=FailingCoverRetriever)
        manga.refresh_from_db()
        manga.baka_info.refresh_from_db()
        self.assertEqual(SHINGEKI_CODE, manga.baka_id)
        self.assertEqual(SHINGEKI_CODE, manga.baka_info.baka_id)
        self.assertEqual(0, manga.baka_info.keywords.count())
        self.assertIn("Refresh failed", output)
        self.assertIn("1 refresh failed", output)

    def test_review_cannot_be_a_dry_run(self):
        with self.assertRaises(CommandError):
            self.review([], "--dry-run")

    def test_refresh_needs_review(self):
        with self.assertRaises(CommandError):
            call_command("convert_old_baka_ids", "--mapping", str(self.mapping_path), "--refresh",
                         stdout=io.StringIO())


class MatchVerdictTests(TestCase):
    @staticmethod
    def verdict(stored_title, title, alternates=(), **kwargs):
        return match_verdict(
            {"title": stored_title, "year": kwargs.get("stored_year"), "people": set(kwargs.get("stored_people", ()))},
            {"title": title, "alternate_titles": list(alternates), "year": kwargs.get("year"),
             "people": set(kwargs.get("people", ()))},
        )

    def test_title_match(self):
        self.assertEqual("MATCH (title)", self.verdict("shingeki  no KYOJIN", "Shingeki no Kyojin"))

    def test_alternate_title_is_partial(self):
        self.assertEqual("PARTIAL (alternate title)", self.verdict("AoT", "Shingeki no Kyojin", ["AoT"]))

    def test_year_and_author_without_title_is_partial(self):
        self.assertEqual(
            "PARTIAL (year, author)",
            self.verdict("Attack on Titan", "Shingeki no Kyojin", stored_year=2009, year=2009,
                         stored_people={"ISAYAMA Hajime"}, people={"ISAYAMA Hajime"}),
        )

    def test_no_match(self):
        self.assertEqual("NO MATCH", self.verdict("Hola", "Shingeki no Kyojin", stored_year=1996, year=2009))

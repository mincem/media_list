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

from ...management.commands.convert_old_baka_ids import MAPPING_URL
from ...models import BakaSeries, MangaSeries

MAPPING = {"47446": "aqw5kar", "2": "tsd1hyz", "88": "zz88zzz"}


class ConvertOldBakaIdsTests(TestCase):
    def setUp(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        self.mapping_path = Path(folder) / "mapping.json"
        self.write_mapping(MAPPING)

    def write_mapping(self, mapping):
        self.mapping_path.write_text(json.dumps(mapping), encoding="utf-8")

    def run_command(self, *args):
        output = io.StringIO()
        call_command("convert_old_baka_ids", "--mapping", str(self.mapping_path), *args, stdout=output)
        return output.getvalue()

    @staticmethod
    def manga(baka_id, info_id=None, title="Some manga"):
        baka_info = BakaSeries.objects.create(baka_id=info_id, title=title) if info_id else None
        return MangaSeries.objects.create(title=title, interest=50, baka_id=baka_id, baka_info=baka_info)

    def test_converts_manga_and_info(self):
        manga = self.manga("47446", info_id="47446")
        self.run_command()
        manga.refresh_from_db()
        manga.baka_info.refresh_from_db()
        self.assertEqual("aqw5kar", manga.baka_id)
        self.assertEqual("aqw5kar", manga.baka_info.baka_id)

    def test_converts_unused_info(self):
        info = BakaSeries.objects.create(baka_id="2", title="Orphan")
        self.run_command()
        info.refresh_from_db()
        self.assertEqual("tsd1hyz", info.baka_id)

    def test_leaves_codes_and_empty_ids_alone(self):
        with_code, without_id = self.manga("aqw5kar"), self.manga(None)
        self.run_command()
        with_code.refresh_from_db()
        without_id.refresh_from_db()
        self.assertEqual("aqw5kar", with_code.baka_id)
        self.assertIsNone(without_id.baka_id)

    def test_reports_and_keeps_unmapped_ids(self):
        manga = self.manga("444666", title="Hola")
        output = self.run_command()
        manga.refresh_from_db()
        self.assertEqual("444666", manga.baka_id)
        self.assertIn("1 numeric IDs are not in the mapping and were kept", output)
        self.assertIn(f"Manga #{manga.pk} 'Hola': 444666", output)

    def test_lists_each_change_with_the_new_url(self):
        manga = self.manga("2", title="Hanazakari no Kimitachi e")
        output = self.run_command()
        self.assertIn(
            f"Manga #{manga.pk} 'Hanazakari no Kimitachi e': 2 -> tsd1hyz  https://www.mangaupdates.com/series/tsd1hyz",
            output,
        )

    def test_dry_run_saves_nothing(self):
        manga = self.manga("47446", info_id="47446")
        output = self.run_command("--dry-run")
        manga.refresh_from_db()
        manga.baka_info.refresh_from_db()
        self.assertEqual("47446", manga.baka_id)
        self.assertEqual("47446", manga.baka_info.baka_id)
        self.assertIn("47446 -> aqw5kar", output)
        self.assertIn("Dry run", output)

    def test_ignores_invalid_mapping_entries(self):
        self.write_mapping({"47446": "aqw5kar", "2": "12345", "88": "not a code", "x": "abc1234"})
        manga = self.manga("2")
        output = self.run_command()
        manga.refresh_from_db()
        self.assertEqual("2", manga.baka_id)
        self.assertIn("not in the mapping", output)

    def test_refuses_mapping_with_duplicate_codes(self):
        self.write_mapping({"47446": "aqw5kar", "2": "aqw5kar"})
        manga = self.manga("2")
        with self.assertRaises(CommandError):
            self.run_command()
        manga.refresh_from_db()
        self.assertEqual("2", manga.baka_id)

    def test_missing_mapping_file(self):
        self.mapping_path.unlink()
        with self.assertRaises(CommandError):
            self.run_command()

    def test_downloads_mapping_without_path(self):
        manga = self.manga("47446")
        response = mock.Mock(**{"json.return_value": MAPPING, "raise_for_status.return_value": None})
        with mock.patch("media_list.management.commands.convert_old_baka_ids.requests.get",
                        return_value=response) as get:
            call_command("convert_old_baka_ids", stdout=io.StringIO())
        get.assert_called_once_with(MAPPING_URL, timeout=60)
        manga.refresh_from_db()
        self.assertEqual("aqw5kar", manga.baka_id)

    def test_failed_download(self):
        with mock.patch("media_list.management.commands.convert_old_baka_ids.requests.get",
                        side_effect=requests.ConnectionError("offline")):
            with self.assertRaises(CommandError):
                call_command("convert_old_baka_ids", stdout=io.StringIO())

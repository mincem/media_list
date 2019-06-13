from django.test import TestCase

from ..utils import OldScanListParser

basara_html = """
        <p class="c4"><span class="c1">
        <a class="c3" href="https://example.com/basara">
        Basara v01-v27 (2003-2007) Complete</a></span>
        </p>
    """
basara_data = {
    "title": "Basara",
    "url": "https://example.com/basara",
    "volumes": 27,
    "has_omnibus": False,
    "is_completed": True,
}

gigantomaxia_html = """
        <p class="c4"><span class="c1">
        <a class="c3" href="https://example.com/gigantomaxia">Giganto Maxia (2016)</a></span>
        </p>
    """

gigantomaxia_data = {
    "title": "Giganto Maxia",
    "url": "https://example.com/gigantomaxia",
    "volumes": 1,
    "has_omnibus": False,
    "is_completed": True,
}


class OldScanListParserTests(TestCase):
    def setUp(self):
        self.parser = OldScanListParser("mock_filename", "Source")

    def test_store_correct_title(self):
        manga_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(basara_data["title"], manga_series.title)

    def test_store_correct_longer_title(self):
        manga_series = self.parser.scan_contents(gigantomaxia_html)[0]
        self.assertEquals(gigantomaxia_data["title"], manga_series.title)

    def test_store_correct_volumes(self):
        manga_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(basara_data["volumes"], manga_series.volumes)

    def test_standalone_stores_one_volume(self):
        manga_series = self.parser.scan_contents(gigantomaxia_html)[0]
        self.assertEquals(gigantomaxia_data["volumes"], manga_series.volumes)

    def test_store_is_completed(self):
        manga_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(True, manga_series.is_completed)

    def test_store_correct_url(self):
        manga_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(basara_data["url"], str(manga_series.urls.first()))

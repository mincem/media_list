from django.test import TestCase

from ..utils import OldScanListParser

basara_html = """
        <p class="c4"><span class="c1">
        <a class="c3" href="http://www.bookgn.com/15817-basara-v01-v27-2003-2007-complete.html">
        Basara v01-v27 (2003-2007) Complete</a></span>
        </p>
    """
basara_data = {
    "title": "Basara",
    "url": "http://www.bookgn.com/15817-basara-v01-v27-2003-2007-complete.html",
    "volumes": 27,
    "has_omnibus": False,
    "is_completed": True,
}

gigantomaxia_html = """
        <p class="c4"><span class="c1">
        <a class="c3" href="http://www.bookgn.com/15222-giganto-maxia-2016.html">Giganto Maxia (2016)</a></span>
        </p>
    """

gigantomaxia_data = {
    "title": "Giganto Maxia",
    "url": "http://www.bookgn.com/15222-giganto-maxia-2016.html",
    "volumes": 1,
    "has_omnibus": False,
    "is_completed": True,
}


class OldScanListParserTests(TestCase):
    def setUp(self):
        self.parser = OldScanListParser("mock_filename")

    def test_store_correct_title(self):
        media_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(basara_data["title"], media_series.title)

    def test_store_correct_longer_title(self):
        media_series = self.parser.scan_contents(gigantomaxia_html)[0]
        self.assertEquals(gigantomaxia_data["title"], media_series.title)

    def test_store_correct_volumes(self):
        media_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(basara_data["volumes"], media_series.volumes)

    def test_standalone_stores_one_volume(self):
        media_series = self.parser.scan_contents(gigantomaxia_html)[0]
        self.assertEquals(gigantomaxia_data["volumes"], media_series.volumes)

    def test_store_is_completed(self):
        media_series = self.parser.scan_contents(basara_html)[0]
        self.assertEquals(True, media_series.is_completed)

from django.test import TestCase

from ..utils.scan_list_parser import ScanListParser

MIN_INTEREST = 0
MAX_INTEREST = 100

strike_the_blood_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
        href="https://example.com/Strike%20the%20Blood"><font color="#1155cc"><font
        face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Strike
  the Blood</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
  (10 tomos, completo, shonen)</font></font></p>
    """

strike_the_blood_data = {
    "title": "Strike the Blood",
    "alternate_title": '',
    "url": "https://example.com/Strike%20the%20Blood",
    "volumes": 10,
    "source": 'E',
    "has_omnibus": False,
    "is_completed": True,
    "interest": 0,
    "notes": "shonen",
}

water_dragon_bride_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
        href="https://example.com/Suijin%20no%20Ikenie"><font color="#783f04"><font
        face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Suijin
  no Hanayome</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
  [The Water Dragon's Bride] (7+ tomos)</font></font></p>
  """

water_dragon_bride_data = {
    "title": "Suijin no Hanayome",
    "alternate_title": "The Water Dragon's Bride",
    "url": "https://example.com/Suijin%20no%20Ikenie",
    "volumes": 7,
    "source": 'E',
    "has_omnibus": False,
    "is_completed": False,
    "interest": 0,
    "notes": "",
}

ceres_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
            href="https://example.com/Ayashi%20no%20Ceres"><font color="#bf9000"><font
            face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Ayashi
      no Ceres</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
      [Ceres Celestial Legend] (14 tomos, completo)&#127775;</font></font></p>
    """

ceres_data = {
    "interest": 100,
}

beauty_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
            href="https://example.com/Bocchi%20Kaibutsu%20to%20Moumoku%20Shoujo"><font
            color="#1155cc"><font face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Bocchi
      Kaibutsu to Moumoku Shoujo</u></font></font></font></a><font face="Arial, serif"><font size="2"
                                                                                             style="font-size: 11pt">
      [Beauty and the Beast Girl] (unitario, yuri)</font></font></p>
    """

dragon_half_html = """
    <p style="margin-bottom: 0cm; border: none; padding: 0cm; line-height: 125%">
    <a href="https://example.com/Dragon%20Half"><font color="#38761d">
    <font face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Dragon
        Half</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
    (3 omnibus, completo)&#127775;</font></font></p>
    """

another_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a href="https://example.com/Another">
    <font color="#1155cc"><font face="Arial, serif"><font size="2" style="font-size: 11pt">
    <u>Another</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
    (omnibus unitario)</font></font></p>
    """


class ScanListParserTests(TestCase):
    def setUp(self):
        self.parser = ScanListParser("mock_filename", "Source")

    def test_reports_amount_scanned(self):
        response = ScanListParser("./media_list/samples/scan_list_test_sample.html", "Source").perform()
        self.assertEquals(2, response["total"])
        self.assertEquals(2, response["created"])
        self.assertEquals(0, len(response["errors"]))

    def test_reports_a_scanning_error(self):
        response = ScanListParser("./media_list/samples/scan_list_broken_test_sample.html", "Source").perform()
        self.assertEquals(2, response["total"])
        self.assertEquals(1, response["created"])
        self.assertEquals(1, len(response["errors"]))

    def test_store_correct_title(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(strike_the_blood_data["title"], manga_series.title)

    def test_store_correct_alternate_title(self):
        manga_series = self.parser.scan_contents(water_dragon_bride_html)[0]
        self.assertEquals(water_dragon_bride_data["alternate_title"], manga_series.alternate_title)

    def test_store_empty_alternate_title(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(strike_the_blood_data["alternate_title"], manga_series.alternate_title)

    def test_store_correct_url(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(strike_the_blood_data["url"], str(manga_series.urls.first()))

    def test_store_correct_volumes(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(strike_the_blood_data["volumes"], manga_series.volumes)

    def test_standalone_stores_one_volume(self):
        manga_series = self.parser.scan_contents(beauty_html)[0]
        self.assertEquals(1, manga_series.volumes)

    def test_store_does_have_omnibus(self):
        manga_series = self.parser.scan_contents(dragon_half_html)[0]
        self.assertEquals(True, manga_series.has_omnibus)

    def test_store_does_not_have_omnibus(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(False, manga_series.has_omnibus)

    def test_store_standalone_omnibus(self):
        manga_series = self.parser.scan_contents(another_html)[0]
        self.assertEquals(1, manga_series.volumes)
        self.assertEquals(True, manga_series.has_omnibus)

    def test_store_is_completed(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(True, manga_series.is_completed)

    def test_store_is_not_completed(self):
        manga_series = self.parser.scan_contents(water_dragon_bride_html)[0]
        self.assertEquals(False, manga_series.is_completed)

    def test_standalone_is_always_completed(self):
        manga_series = self.parser.scan_contents(beauty_html)[0]
        self.assertEquals(True, manga_series.is_completed)

    def test_store_min_interest(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals(MIN_INTEREST, manga_series.interest)

    def test_store_max_interest(self):
        manga_series = self.parser.scan_contents(ceres_html)[0]
        self.assertEquals(MAX_INTEREST, manga_series.interest)

    def test_store_status_not_downloaded(self):
        manga_series = self.parser.scan_contents(strike_the_blood_html)[0]
        self.assertEquals("N", manga_series.status)

    def test_store_status_downloading(self):
        manga_series = self.parser.scan_contents(water_dragon_bride_html)[0]
        self.assertEquals("D", manga_series.status)

    def test_store_status_downloaded_raw(self):
        manga_series = self.parser.scan_contents(ceres_html)[0]
        self.assertEquals("R", manga_series.status)

    def test_store_status_edited(self):
        manga_series = self.parser.scan_contents(dragon_half_html)[0]
        self.assertEquals("E", manga_series.status)

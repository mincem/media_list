from django.test import TestCase

from ..utils import ScanListParser

MIN_INTEREST = 0
MAX_INTEREST = 100

strike_the_blood_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
        href="https://manga.madokami.al/Manga/S/ST/STRI/Strike%20the%20Blood"><font color="#1155cc"><font
        face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Strike
  the Blood</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
  (10 tomos, completo, shonen)</font></font></p>
    """

strike_the_blood_data = {
    "title": "Strike the Blood",
    "alternate_title": '',
    "url": "https://manga.madokami.al/Manga/S/ST/STRI/Strike%20the%20Blood",
    "volumes": 10,
    "source": 'E',
    "has_omnibus": False,
    "is_completed": True,
    "interest": 0,
    "notes": "shonen",
}

water_dragon_bride_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
        href="https://manga.madokami.al/Manga/S/SU/SUIJ/Suijin%20no%20Ikenie"><font color="#1155cc"><font
        face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Suijin
  no Hanayome</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
  [The Water Dragon's Bride] (7+ tomos)</font></font></p>
  """

water_dragon_bride_data = {
    "title": "Suijin no Hanayome",
    "alternate_title": "The Water Dragon's Bride",
    "url": "https://manga.madokami.al/Manga/S/SU/SUIJ/Suijin%20no%20Ikenie",
    "volumes": 7,
    "source": 'E',
    "has_omnibus": False,
    "is_completed": False,
    "interest": 0,
    "notes": "",
}

ceres_html = """
    <p style="margin-bottom: 0cm; line-height: 125%"><a
            href="https://manga.madokami.al/Manga/A/AY/AYAS/Ayashi%20no%20Ceres"><font color="#1155cc"><font
            face="Arial, serif"><font size="2" style="font-size: 11pt"><u>Ayashi
      no Ceres</u></font></font></font></a><font face="Arial, serif"><font size="2" style="font-size: 11pt">
      [Ceres Celestial Legend] (14 tomos, completo)&#127775;</font></font></p>
    """

ceres_data = {
    "interest": 100,
}


class ScanListParserTests(TestCase):
    def test_store_correct_title(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.title, strike_the_blood_data["title"])

    def test_store_correct_alternate_title(self):
        media_series = ScanListParser().scan_contents(water_dragon_bride_html)[0]
        self.assertEquals(media_series.alternate_title, water_dragon_bride_data["alternate_title"])

    def test_store_empty_alternate_title(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.alternate_title, strike_the_blood_data["alternate_title"])

    def test_store_correct_url(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.url, strike_the_blood_data["url"])

    def test_store_correct_volumes(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.volumes, strike_the_blood_data["volumes"])

    def test_store_does_have_omnibus(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.has_omnibus, True)

    def test_store_does_not_have_omnibus(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.has_omnibus, False)

    def test_store_is_completed(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.is_completed, True)

    def test_store_is_not_completed(self):
        media_series = ScanListParser().scan_contents(water_dragon_bride_html)[0]
        self.assertEquals(media_series.is_completed, False)

    def test_store_min_interest(self):
        media_series = ScanListParser().scan_contents(strike_the_blood_html)[0]
        self.assertEquals(media_series.interest, MIN_INTEREST)

    def test_store_max_interest(self):
        media_series = ScanListParser().scan_contents(ceres_html)[0]
        self.assertEquals(media_series.interest, MAX_INTEREST)

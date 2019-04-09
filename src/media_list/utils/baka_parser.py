import json

from bs4 import BeautifulSoup
from ..models import BakaSeries


class BakaParser:
    def __init__(self, baka_id):
        self.baka_id = baka_id
        self.raw_data = None

    def baka_series(self):
        return print(json.dumps(self._parse_webpage(), indent=2))
        # return BakaSeries.objects.create()

    def _parse_webpage(self):
        soup = BeautifulSoup(self._raw_data())
        main_content = soup.find(id="main_content")
        contents = self._find_contents(main_content)
        return {
            "title": self.parse_title(main_content),
            "description": self.parse_description(main_content),
            "author": contents["Author(s)"],
            "artist": contents["Artist(s)"],
            "year": contents["Year"],
            "original_publisher": contents["Original Publisher"],
            "english_publisher": contents["English Publisher"],
        }

    @staticmethod
    def parse_description(soup):
        return ' '.join(soup.find(id="div_desc_more").stripped_strings)  # TODO: Description format

    @staticmethod
    def parse_title(soup):
        return soup.find(class_="releasestitle").string

    def _raw_data(self):
        if self.raw_data is None:
            self.raw_data = self._baka_webpage()
        return self.raw_data

    @staticmethod
    def _baka_webpage():
        with open("./media_list/samples/sample_baka.html", 'rb') as html_file:
            dump = html_file.read()
        return dump

    def _find_contents(self, soup):
        cat_ = {self._category_name(category): self._category_content(category) for category in soup(class_="sCat")}
        print(json.dumps(cat_, indent=2))
        return cat_

    @staticmethod
    def _category_name(category):
        return category.string

    @staticmethod
    def _category_content(category):
        return category.find_next_sibling(class_="sContent").string

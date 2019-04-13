import json

import requests
from bs4 import BeautifulSoup
from ..models import BakaSeries


class BakaParser:
    def __init__(self, baka_retriever=None):
        self.baka_retriever = baka_retriever or BakaRetriever()

    def baka_series(self, baka_id):
        return BakaSeries.objects.create(**self.parsed_series_data(baka_id))

    def display_parsed_data(self, baka_id):
        return json.dumps(self.parsed_series_data(baka_id), indent=2)

    def parsed_series_data(self, baka_id):
        soup = BeautifulSoup(self.baka_web_page_html(baka_id), "lxml")
        main_content = soup.find(id="main_content")
        contents = all_contents(main_content)
        return {
            "title": parse_title(main_content),
            "description": parse_description(main_content),
            "author": contents["Author(s)"],
            "artist": contents["Artist(s)"],
            "year": int(clean(contents["Year"])),
            "original_publisher": contents["Original Publisher"],
            "english_publisher": contents["English Publisher"],
        }

    def baka_web_page_html(self, baka_id):
        return self.baka_retriever.get(baka_id)


def all_contents(soup):
    return {name_of(category): content_of(category) for category in soup(class_="sCat")}


def name_of(category):
    return category.string


def content_of(category):
    return category.find_next_sibling(class_="sContent").string


def parse_title(soup):
    return soup.find(class_="releasestitle").string


def parse_description(soup):
    description_tag = soup.find(id="div_desc_more")
    if description_tag is None:
        return ""
    return clean_text(description_tag)  # TODO: Description format


def clean_text(html_tag):
    return clean(" ".join(html_tag.stripped_strings))


def clean(text):
    return " ".join(text.split())


class BakaRetriever:
    def get(self, baka_id):
        response = requests.get(f"https://www.mangaupdates.com/series.html?id={baka_id}")
        response.raise_for_status()
        return response.text


class MockBakaRetriever(BakaRetriever):
    def get(self, _baka_id):
        with open("./media_list/samples/sample_baka.html", 'rb') as html_file:
            dump = html_file.read()
        return dump

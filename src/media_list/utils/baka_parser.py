import json

import requests
from bs4 import BeautifulSoup
from ..models import BakaSeries, MangaPerson, MangaGenre


class BakaParser:
    def __init__(self, baka_id, baka_retriever=None):
        self.baka_id = baka_id
        self.baka_retriever = baka_retriever or BakaRetriever()
        self.web_page_html = None

    def perform(self):
        parsed_series_data = self.parsed_series_data()
        author = create_person(parsed_series_data.pop("author_name", None))
        artist = create_person(parsed_series_data.pop("artist_name", None))
        genres = create_genres(parsed_series_data.pop("genre_names", None))
        baka_series = BakaSeries.objects.create(
            **parsed_series_data,
            author=author,
            artist=artist,
        )
        baka_series.genres.add(*genres)
        return baka_series

    def display_parsed_data(self):
        return json.dumps(self.parsed_series_data(), indent=2)

    def parsed_series_data(self):
        soup = BeautifulSoup(self.baka_web_page_html(), "lxml")
        main_content = soup.find(id="main_content")
        contents = all_contents(main_content)
        return {
            "baka_id": self.baka_id,
            "title": parse_title(main_content),
            "genre_names": parse_genres(contents["Genre"]) or [],
            "description": parse_description(main_content),
            "status": clean_text(contents["Status in Country of Origin"]),
            "author_name": parse_person_name(contents["Author(s)"]),
            "artist_name": parse_person_name(contents["Artist(s)"]),
            "year": int(clean_text(contents["Year"])) or None,
            "original_publisher": clean_text(contents["Original Publisher"]) or "",
            "english_publisher": clean_text(contents["English Publisher"]) or "",
            "image": None,
        }

    def baka_web_page_html(self):
        if self.web_page_html is None:
            self.web_page_html = self.baka_retriever.get(self.baka_id)
        return self.web_page_html


def all_contents(soup):
    return {name_of(category): html_of(category) for category in soup(class_="sCat")}


def name_of(category):
    return " ".join(category.stripped_strings)


def html_of(category):
    return category.find_next_sibling(class_="sContent")


def parse_title(soup):
    return soup.find(class_="releasestitle").string


def parse_description(soup):
    description_tag = soup.find(id="div_desc_more")
    if description_tag is None:
        return ""
    description_tag.a.extract()
    return clean_text(description_tag)


def parse_person_name(html):
    if html is None:
        return None
    return html.find("a").string


def parse_genres(html):
    if html is None:
        return None
    html.br.find_next_sibling().extract()
    return list(html.stripped_strings)


def clean_text(html_tag):
    return clean(" ".join(html_tag.stripped_strings))


def clean(text):
    return " ".join(text.split())


def create_person(name):
    if name is None:
        return None
    author, _created = MangaPerson.objects.get_or_create(name=name)
    return author


def create_genres(names):
    return [MangaGenre.objects.get_or_create(name=genre_name)[0] for genre_name in names]


class BakaRetriever:
    @staticmethod
    def get(baka_id):
        response = requests.get(f"https://www.mangaupdates.com/series.html?id={baka_id}")
        response.raise_for_status()
        return response.text

import json
import os
import re

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from ..models import BakaSeries, MangaPerson, MangaGenre, MangaKeyword


class BakaParser:
    def __init__(self, baka_id, baka_retriever=None, image_retriever=None):
        self.baka_id = baka_id
        self.baka_retriever = baka_retriever or BakaRetriever()
        self.image_retriever = image_retriever or BakaImageRetriever()
        self.web_page_html = None

    def perform(self):
        parsed_series_data = self.parsed_series_data()
        authors = create_people(parsed_series_data.pop("author_names", None))
        artists = create_people(parsed_series_data.pop("artist_names", None))
        genres = create_genres(parsed_series_data.pop("genre_names", None))
        keywords_data = parsed_series_data.pop("keywords", None)
        image_data = parsed_series_data.pop("image", None)
        baka_series = BakaSeries.objects.create(**parsed_series_data)
        baka_series.genres.add(*genres)
        baka_series.authors.add(*authors)
        baka_series.artists.add(*artists)
        add_keywords(keywords_data, baka_series)
        if image_data is not None:
            baka_series.image.save(**image_data)
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
            "keywords": parse_keywords(contents["Categories"]) or [],
            "description": parse_description(main_content, contents),
            "status": clean_text(contents["Status in Country of Origin"]),
            "author_names": parse_person_names(contents["Author(s)"]),
            "artist_names": parse_person_names(contents["Artist(s)"]),
            "year": int(clean_text(contents["Year"])) or None,
            "original_publisher": clean_text(contents["Original Publisher"]) or "",
            "english_publisher": clean_text(contents["English Publisher"]) or "",
            "image": self.parse_image(contents["Image [ Report Inappropriate Content ]"]),
        }

    def baka_web_page_html(self):
        if self.web_page_html is None:
            self.web_page_html = self.baka_retriever.get(self.baka_id)
        return self.web_page_html

    def parse_image(self, html_tag):
        if html_tag.img is None:
            return None
        image_url = html_tag.img["src"]
        return self.image_retriever.get(image_url)


def all_contents(soup):
    return {name_of(category): html_of(category) for category in soup(class_="sCat")}


def name_of(category):
    return " ".join(category.stripped_strings)


def html_of(category):
    return category.find_next_sibling(class_="sContent")


def parse_title(soup):
    return soup.find(class_="releasestitle").string


def parse_description(soup, contents):
    description_tag = soup.find(id="div_desc_more")
    if description_tag is None:
        description_tag = contents["Description"]
    else:
        description_tag.find_all("a")[-1].extract()
    return clean_text(description_tag)


def parse_person_names(html):
    if html is None:
        return []
    return [hyperlink.string for hyperlink in html.find_all("a")]


def parse_genres(html):
    if html is None:
        return None
    html.br.find_next_sibling().extract()
    return list(html.stripped_strings)


def parse_keywords(html):
    if html is None:
        return None
    return [parse_keyword(item) for item in html.find("ul").find_all("li")]


def parse_keyword(html):
    return {
        "name": html.text,
        "score": re.search(r'Score: (.*) \(', html.a.attrs["title"]).group(1)
    }


def clean_text(html_tag):
    return clean(" ".join(html_tag.stripped_strings))


def clean(text):
    return " ".join(text.split())


def create_people(names):
    return [MangaPerson.objects.get_or_create(name=name)[0] for name in names]


def create_genres(names):
    return [MangaGenre.objects.get_or_create(name=genre_name)[0] for genre_name in names]


def add_keywords(keywords_data, baka_series):
    for keyword_data in keywords_data:
        keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
        baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})


class BakaRetriever:
    @staticmethod
    def get(baka_id):
        response = requests.get(f"https://www.mangaupdates.com/series.html?id={baka_id}")
        response.raise_for_status()
        return response.text


class BakaImageRetriever:
    @staticmethod
    def get(baka_image_url):
        response = requests.get(baka_image_url)
        response.raise_for_status()
        return {
            "name": os.path.basename(baka_image_url),
            "content": ContentFile(response.content),
        }

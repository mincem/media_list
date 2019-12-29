import re

from bs4 import BeautifulSoup


class BakaPageScraper:
    def __init__(self, page_html, baka_id):
        self.baka_id = baka_id
        self.main_content = BeautifulSoup(page_html, "lxml").find(id="main_content")
        self.contents = self.all_contents()

    def all_contents(self):
        return {name_of(category): html_of(category) for category in self.main_content(class_="sCat")}

    def parse(self):
        return {
            "baka_id": self.baka_id,
            "title": self.parse_title(),
            "genre_names": self.parse_genres(),
            "keywords": self.parse_keywords(),
            "description": self.parse_description(),
            "status": self.parse_status(),
            "author_names": self.parse_authors(),
            "artist_names": self.parse_artists(),
            "year": int(clean_text(self.contents["Year"])) or None,
            "original_publisher": clean_text(self.contents["Original Publisher"]) or "",
            "english_publisher": clean_text(self.contents["English Publisher"]) or "",
            "image_url": self.parse_image_url(),
        }

    def parse_title(self):
        return self.main_content.find(class_="releasestitle").string

    def parse_genres(self):
        genres = self.contents["Genre"]
        if genres is None:
            return []
        genres.br.find_next_sibling().extract()
        return list(genres.stripped_strings)

    def parse_keywords(self):
        keywords = self.contents["Categories"]
        if keywords is None:
            return []
        return [self.parse_keyword(item) for item in keywords.find("ul").find_all("li")]

    @staticmethod
    def parse_keyword(html):
        return {
            "name": clean(html.text),
            "score": re.search(r'Score: (.*) \(', html.a.attrs["title"]).group(1)
        }

    def parse_description(self):
        description_tag = self.main_content.find(id="div_desc_more")
        if description_tag is None:
            description_tag = self.contents["Description"]
        else:
            description_tag.find_all("a")[-1].extract()
        return clean_text(description_tag)

    def parse_status(self):
        return clean_text(self.contents["Status in Country of Origin"])

    def parse_authors(self):
        return self.parse_person_names(section="Author(s)")

    def parse_artists(self):
        return self.parse_person_names(section="Artist(s)")

    def parse_person_names(self, section):
        section_html = self.contents[section]
        if section_html is None:
            return []
        return [hyperlink.string for hyperlink in section_html.find_all("a")]

    def parse_image_url(self):
        html_tag = self.contents["Image [ Report Inappropriate Content ]"]
        if html_tag.img is None:
            return None
        return html_tag.img["src"]


def name_of(category):
    return " ".join(category.stripped_strings)


def html_of(category):
    return category.find_next_sibling(class_="sContent")


def clean_text(html_tag):
    return clean(" ".join(html_tag.stripped_strings))


def clean(text):
    return " ".join(text.split())

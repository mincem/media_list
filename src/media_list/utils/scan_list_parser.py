import os
import re

from bs4 import BeautifulSoup

from ..models import MangaSeries, MangaSource, MangaURL

STAR_EMOJI = "🌟"

DEFAULT_STATUS = "U"
LINK_COLORS = {
    "#1155cc": "N",
    "#783f04": "D",
    "#bf9000": "R",
    "#38761d": "E",
}


class ScanListParser:
    def __init__(self, filename, source_name):
        self.filename = filename
        self.source = MangaSource.objects.get_or_create(name=source_name)[0]
        self.total_lines_read = 0
        self.series_created = 0
        self.errors = []

    def perform(self):
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f'File "{self.filename}" does not exist.')
        with open(self.filename, 'rb') as html_file:
            self.scan_contents(html_file)
        return {
            "total": self.total_lines_read,
            "created": self.series_created,
            "errors": self.errors
        }

    def scan_contents(self, html):
        soup = BeautifulSoup(html, "lxml")
        return [self.scan(entry) for entry in soup("p")]

    def scan(self, entry):
        try:
            extracted_data = self.extracted_data_from(entry)
            url = extracted_data.pop("url", None)
            series = MangaSeries.objects.create(**extracted_data)
            if url is not None:
                create_manga_url(url, series)
            self.series_created += 1
            self.total_lines_read += 1
            return series
        except Exception as error:
            self.errors.append({"line": entry, "error": error})
            self.total_lines_read += 1
            return None

    def extracted_data_from(self, entry):
        line = clean_text(entry)
        return {
            "title": parse_title(line, entry),
            "alternate_title": find_alternate_title(line),
            "url": parse_url(entry),
            "volumes": find_volumes(line),
            "source": self.source,
            "has_omnibus": "omnibus" in line,
            "is_completed": "completo" in line or "unitario" in line,
            "interest": 100 if STAR_EMOJI in line else 0,
            "status": find_status(entry),
            "notes": "",
        }


class OldScanListParser(ScanListParser):
    def extracted_data_from(self, entry):
        line = clean_text(entry)
        return {
            "title": parse_old_title(line),
            "alternate_title": "",
            "url": parse_url(entry),
            "volumes": find_old_volumes(line),
            "source": self.source,
            "has_omnibus": "omnibus" in line.lower(),
            "is_completed": "complete" in line.lower(),
            "interest": 100 if STAR_EMOJI in line else 0,
            "status": find_status(entry),
            "notes": "",
        }


def clean_text(html_tag):
    soup_string = " ".join(html_tag.stripped_strings)
    return " ".join(soup_string.split())


def parse_url(entry):
    hyperlink = entry.find("a")
    return None if hyperlink is None else hyperlink.get("href")


def parse_title(line, entry):
    hyperlink = entry.find("a")
    if hyperlink is None:
        return re.search(r'(.*?) [(\[]', line).group(1)
    return clean_text(hyperlink)


def parse_old_title(line):
    return re.search(r'(.*?) (Omnibus|v[0-9]|\()', line).group(1)


def find_alternate_title(line):
    if "[" not in line:
        return ""
    return line[line.find("[") + 1:line.find("]")]


def find_volumes(line):
    if "unitario" in line:
        return 1
    match = re.search(r'.*\((.*?)(\+?) (tomos|omnibus)', line)
    return int(match.group(1))


def find_old_volumes(line):
    match = re.findall(r'v[0-9]{1,2}', line)
    if not match:
        return 1
    return int(match[-1].replace("v", ""))


def find_status(entry):
    entry_html = str(entry)
    try:
        return next(status for color, status in LINK_COLORS.items() if color in entry_html)
    except StopIteration:
        return DEFAULT_STATUS


def create_manga_url(url, series):
    if url is None:
        return None
    return MangaURL.objects.create(url=url, series=series)

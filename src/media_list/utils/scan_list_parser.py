import os
import re

from bs4 import BeautifulSoup

from ..models import MediaSeries, MangaSource

STAR_EMOJI = "🌟"

DEFAULT_STATUS = "U"
LINK_COLORS = {
    "#1155cc": "N",
    "#783f04": "D",
    "#bf9000": "R",
    "#38761d": "E",
}


class ScanListParser:
    def __init__(self, filename):
        self.filename = filename
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
            series = MediaSeries.objects.create(**self.extracted_data_from(entry))
            self.series_created += 1
            self.total_lines_read += 1
            return series
        except Exception as error:
            self.errors.append({"line": entry, "error": error})
            self.total_lines_read += 1

    @staticmethod
    def extracted_data_from(entry):
        line = entry_contents(entry)
        return {
            "title": parse_title(line),
            "alternate_title": find_alternate_title(line),
            "url": parse_url(entry),
            "volumes": find_volumes(line),
            "source": MangaSource.objects.first() or None,
            "has_omnibus": "omnibus" in line,
            "is_completed": "completo" in line or "unitario" in line,
            "interest": 100 if STAR_EMOJI in line else 0,
            "status": find_status(entry),
            "notes": "",
        }


def entry_contents(entry):
    soup_string = " ".join(entry.stripped_strings)
    return " ".join(soup_string.split())


def parse_url(entry):
    hyperlink = entry.find("a")
    return None if hyperlink is None else hyperlink.get("href")


def parse_title(line):
    return re.search(r'(.*?) [(\[]', line).group(1)


def find_alternate_title(line):
    if "[" not in line:
        return ""
    return line[line.find("[") + 1:line.find("]")]


def find_volumes(line):
    if "unitario" in line:
        return 1
    match = re.search(r'\((.*?)(\+?) (tomos|omnibus)', line)
    return int(match.group(1))


def find_status(entry):
    entry_html = str(entry)
    try:
        entry_text_color = next(color for color in (LINK_COLORS.keys()) if color in entry_html)
        return LINK_COLORS[entry_text_color]
    except StopIteration:
        return DEFAULT_STATUS

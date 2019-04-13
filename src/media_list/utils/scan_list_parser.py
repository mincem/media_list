import re

from bs4 import BeautifulSoup

from ..models import MediaSeries

STAR_EMOJI = "🌟"


class ScanListParser:
    def scan(self):
        with open("./media_list/samples/scans_sample.html", 'rb') as html_file:
            self.scan_contents(html_file)

    def scan_contents(self, html):
        soup = BeautifulSoup(html, "lxml")
        return [self.store(self.extracted_data_from(entry)) for entry in soup("p")]

    @staticmethod
    def extracted_data_from(entry):
        url = parse_url(entry)
        line = entry_contents(entry)
        title = re.search(r'(.*?) [(\[]', line).group(1)
        alternate_title = line[line.find("[") + 1:line.find("]")] if "[" in line else ''
        match = re.search(r'\((.*?)(\+?) (tomos|omnibus)', line)
        volumes = 1 if "unitario" in line else int(match.group(1))
        omnibus = "omnibus" in line
        is_completed = "completo" in line
        interest = 100 if STAR_EMOJI in line else 0
        return {
            "title": title,
            "alternate_title": alternate_title,
            "url": url,
            "volumes": volumes,
            "source": 'E',
            "has_omnibus": omnibus,
            "is_completed": is_completed,
            "interest": interest,
            "notes": "",
        }

    @staticmethod
    def store(series_data):
        return MediaSeries.objects.create(**series_data)


def entry_contents(entry):
    soup_string = " ".join(entry.stripped_strings)
    return " ".join(soup_string.split())


def parse_url(entry):
    hyperlink = entry.find("a")
    return None if hyperlink is None else hyperlink.get("href")

import re

from bs4 import BeautifulSoup

from ..models import MediaSeries

STAR_EMOJI = "🌟"


class ScanListParser:
    def scan(self):
        with open("./media_list/samples/scans_sample.html", 'rb') as html_file:
            soup = BeautifulSoup(html_file)
            parsed_entries = [self.parsed_entry(entry) for entry in soup("p")]
            self.store_entries(parsed_entries)

    @staticmethod
    def store_entries(entries):
        for entry in entries:
            MediaSeries.objects.create(**entry)

    def parsed_entry(self, entry):
        url = self.parse_url(entry)
        line = self.entry_contents(entry)
        title = re.search(r'(.*?) [(\[]', line).group(1)
        alternate_title = line[line.find("[") + 1:line.find("]")] if "[" in line else ''
        match = re.search(r'\((.*?)(\+?) (tomos|omnibus)', line)
        volumes = 1 if "unitario" in line else match.group(1)
        omnibus = match is not None and "omnibus" in match.group(3)  # TODO: "omnibus" "unitario"
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
    def parse_url(entry):
        hyperlink = entry.find("a")
        return None if hyperlink is None else hyperlink.get("href")

    @staticmethod
    def entry_contents(entry):
        soup_string = " ".join(entry.stripped_strings)
        return " ".join(soup_string.split())

import os
import re

from django.core.management.base import BaseCommand

from ...models import MangaSource, MangaSeries


class Command(BaseCommand):
    help = 'Imports manga series from a list of Markdown links'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('source', type=str)

    def handle(self, *args, **options):
        self.source = MangaSource.objects.get_or_create(name=options["source"])[0]
        self.parse(options["file"])

    def print_dividing_line(self):
        self.stdout.write(self.style.ERROR("----------------------------------------------------"))

    def parse(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError(f'File "{filename}" does not exist.')
        with open(filename, 'r', encoding="utf8") as html_file:
            for line in html_file:
                self.scan_contents(line)
                self.print_dividing_line()

    def scan_contents(self, line):
        for match in matches_in_line(line):
            self.stdout.write(f"text: {match['text']}")
            entry = parse_entry(match["text"], match["url"])
            if entry is None:
                self.stdout.write("No data extracted")
                return
            self.print_entry(entry)
            self.process_manga(entry)

    def print_entry(self, entry):
        self.stdout.write(f"url: {entry['link']}")
        self.stdout.write(f"title: {entry['title']}")
        self.stdout.write(f"volumes: {entry['volumes']}")
        best_match = next(iter(entry["matches"]), None)
        if best_match:
            self.stdout.write(f"best match: {best_match} ({best_match.volumes} volumes)")

    def process_manga(self, entry):
        volumes = entry["volumes"]
        best_match = next(iter(entry["matches"]), None)
        if best_match:
            answer = input("Update best match? ('v' ignores volumes)\n")
            if answer == 'v':
                volumes = 0
            if answer in ['y', 'v']:
                return update_best_match(best_match, volumes, entry["link"])
        answer = input("Add new manga? ('v' ignores volumes)\n")
        if answer == 'v':
            volumes = 0
        if answer in ['y', 'v']:
            return self.save_new_manga(entry["title"], volumes, entry["link"])

    def save_new_manga(self, title, volumes, url):
        manga = MangaSeries.objects.create(
            title=title,
            volumes=volumes,
            interest=0,
            status='N',
            source=self.source
        )
        add_url(manga, url)


def matches_in_line(line):
    markdown_link_pattern = re.compile(r"\[([\w\W\s\d]+?)\]\(((?:/|https?://)[\w\W\s\d./?=#]+)\)")
    return [{"text": match.group(1), "url": match.group(2)} for match in re.finditer(markdown_link_pattern, line)]


def parse_entry(text, url):
    full_text, title, volumes = parse_text(text)
    if not title:
        return None
    return {
        "full_text": full_text,
        "link": url,
        "title": title,
        "volumes": volumes,
        "matches": [manga_best_match(title)]
    }


def parse_text(text):
    pattern = re.compile(r"(.*?)\(?[ v[\d]+-?v?([\d]+)]?")
    match = re.match(pattern, text)
    if match is None:
        return
    full_text = match.group(0)
    title = match.group(1).strip()
    volumes = int(match.group(2)) if match.group(2) else 0
    return full_text, title, volumes


def manga_best_match(title):
    query = MangaSeries.objects.filter(title__icontains=title) | \
            MangaSeries.objects.filter(alternate_title__icontains=title)
    return query.first()


def update_best_match(best_match, volumes, url):
    if int(volumes) > 0:
        best_match.volumes = volumes
        best_match.save()
    add_url(best_match, url)


def add_url(manga, url):
    manga.urls.get_or_create(url=url)

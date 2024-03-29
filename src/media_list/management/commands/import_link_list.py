import os

from django.core.management.base import BaseCommand

from ...models import MangaSource, MangaSeries
from ...parsers import link_list_parser


class Command(BaseCommand):
    help = 'Imports manga series from a list of Markdown links'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = None

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
        for entry in link_list_parser.entries_in_line(line):
            if entry is None:
                self.stdout.write("No data extracted")
                return
            self.print_entry(entry)
            self.process_manga(entry)

    def print_entry(self, entry):
        self.stdout.write(f"text: {entry['full_text']}")
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
                update_best_match(best_match, volumes, entry["link"])
                return
        answer = input("Add new manga? ('v' ignores volumes)\n")
        if answer == 'v':
            volumes = 0
        if answer in ['y', 'v']:
            self.save_new_manga(entry["title"], volumes, entry["link"])

    def save_new_manga(self, title, volumes, url):
        manga = MangaSeries.objects.create(
            title=title,
            volumes=volumes,
            interest=0,
            status='N',
            source=self.source
        )
        add_url(manga, url)


def update_best_match(best_match, volumes, url):
    if int(volumes) > 0:
        best_match.volumes = volumes
        best_match.save()
    add_url(best_match, url)


def add_url(manga, url):
    manga.urls.get_or_create(url=url)

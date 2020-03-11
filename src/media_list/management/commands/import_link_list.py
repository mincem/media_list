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

    def scan_contents(self, line):
        markdown_link_pattern = re.compile(r"\[([\w\W\s\d]+?)\]\(((?:/|https?://)[\w\d./?=#]+)\)")
        for match in re.finditer(markdown_link_pattern, line):
            self.parse_entry(
                text=match.group(1),
                url=match.group(2)
            )
        self.print_dividing_line()

    def parse_entry(self, text, url):
        full_text, title, volumes = parse_text(text)
        print(f"text: {text}")
        if not title:
            print("No data extracted")
            return
        print(f"title: {title}")
        print(f"volumes: {volumes}")
        best_match = manga_best_match(title)
        if best_match:
            print(f"best match: {best_match} ({best_match.volumes} volumes)")
        self.process_manga(title, volumes, url, best_match)

    def process_manga(self, title, volumes, url, best_match):
        if best_match:
            answer = input("Update best match? ('v' ignores volumes)\n")
            if answer == 'v':
                volumes = 0
            if answer in ['y', 'v']:
                return update_best_match(best_match, volumes, url)
        answer = input("Add new manga? ('v' ignores volumes)\n")
        if answer == 'v':
            volumes = 0
        if answer in ['y', 'v']:
            return self.save_new_manga(title, volumes, url)

    def save_new_manga(self, title, volumes, url):
        manga = MangaSeries.objects.create(
            title=title,
            volumes=volumes,
            interest=0,
            status='N',
            source=self.source
        )
        add_url(manga, url)


def parse_text(text):
    pattern = re.compile(r"(.*?)\(?[ v[\d]+-?([\d]+)]?")
    match = re.match(pattern, text)
    if match is None:
        return
    full_text = match.group(0)
    title = match.group(1)
    volumes = match.group(2)
    return full_text, title, volumes


def manga_best_match(title):
    query = MangaSeries.objects.filter(title__icontains=title) | \
            MangaSeries.objects.filter(alternate_title__icontains=title)
    return query.first()


def update_best_match(best_match, volumes, url):
    if volumes > 0:
        best_match.volumes = volumes
        best_match.save()
    add_url(best_match, url)


def add_url(manga, url):
    manga.urls.get_or_create(url=url)

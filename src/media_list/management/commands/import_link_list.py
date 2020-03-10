import os
import re

from django.core.exceptions import ObjectDoesNotExist
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
        with open(filename, 'r') as html_file:
            for line in html_file:
                self.scan_contents(line)

    def scan_contents(self, line):
        markdown_link_pattern = re.compile(r"\[([\w\W\s\d]+?)\]\(((?:/|https?://)[\w\d./?=#]+)\)")
        for match in re.finditer(markdown_link_pattern, line):
            parse_entry(
                text=match.group(1),
                url=match.group(2)
            )
        self.print_dividing_line()


def parse_entry(text, url):
    full_text, title, volumes = parse_text(text)
    print(f"text: {full_text}")
    if not title:
        print("No data extracted")
        return
    print(f"title: {title}")
    print(f"volumes: {volumes}")
    best_match = manga_best_match(title)
    if best_match:
        print(f"best match: {best_match} ({best_match.volumes} volumes)")
    answer = input("Proceed?\n")
    if answer == 'y':
        process_manga(title, volumes, url, best_match)


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
    try:
        return MangaSeries.objects.get(title__icontains=title)
    except ObjectDoesNotExist:
        try:
            return MangaSeries.objects.get(alternate_title__icontains=title)
        except ObjectDoesNotExist:
            return


def process_manga(title, volumes, url, best_match):
    if best_match:
        add_url(best_match, url)
    else:
        save_new_manga(title, volumes, url)


def save_new_manga(title, volumes, url):
    manga = MangaSeries.objects.create(
        title=title,
        volumes=volumes,
        interest=0,
        status='N',
    )
    add_url(manga, url)


def add_url(manga, url):
    manga.urls.create(url=url)

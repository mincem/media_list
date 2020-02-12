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
        results = self.parse(options["file"], options["source"])

    def print_dividing_line(self):
        self.stdout.write(self.style.ERROR("----------------------------------------------------"))

    def parse(self, filename, source_name):
        source = MangaSource.objects.get_or_create(name=source_name)[0]
        if not os.path.isfile(filename):
            raise FileNotFoundError(f'File "{filename}" does not exist.')
        with open(filename, 'r') as html_file:
            for line in html_file:
                self.scan_contents(line)

    def scan_contents(self, line):
        markdown_link_pattern = re.compile(r"\[([\w\W\s\d]+?)\]\(((?:/|https?://)[\w\d./?=#]+)\)")
        for match in re.finditer(markdown_link_pattern, line):
            text = match.group(1)
            url = match.group(2)
            full_text, title, volumes = self.parse_text(text)
            if title:
                print(f"text: {full_text}")
                print(f"title: {title}")
                print(f"volumes: {volumes}")

                manga_best_match = self.best_match(title)
                answer = input("Proceed?\n")
                if answer == 'y':
                    if manga_best_match:
                        self.add_url(manga_best_match, "")

        self.print_dividing_line()

    def parse_text(self, text):
        pattern = re.compile(r"(.*?)\(?[ v[\d]+-?([\d]+)]?")
        match = re.match(pattern, text)
        if match is None:
            return
        full_text = match.group(0)
        title = match.group(1)
        volumes = match.group(2)
        return full_text, title, volumes

    def best_match(self, title):
        try:
            manga = MangaSeries.objects.get(title__icontains=title)
        except ObjectDoesNotExist:
            try:
                manga = MangaSeries.objects.get(alternate_title__icontains=title)
            except ObjectDoesNotExist:
                manga = None
        if manga:
            print(f"best match: {manga} ({manga.volumes} volumes)")
        return manga

    def add_url(self, manga, url):
        manga.urls.create(url=url)

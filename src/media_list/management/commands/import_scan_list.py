from django.core.management.base import BaseCommand

from ...utils import ScanListParser


class Command(BaseCommand):
    help = 'Imports manga series from a list of scans'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('source', type=str)

    def handle(self, *args, **options):
        results = ScanListParser(options["file"], options["source"]).perform()
        self.print_parsing_results(results["created"], results["total"])
        self.print_parsing_errors(results["errors"])

    def print_parsing_results(self, created, total):
        self.stdout.write(self.style.SUCCESS(
            f"Finished importing list. Created {created} series from {total} lines."
        ))

    def print_parsing_errors(self, errors):
        if errors:
            self.stdout.write(self.style.ERROR(f"Found {len(errors)} errors:\n"))
            self.print_dividing_line()
        for error in errors:
            self.print_parsing_error(exception=error["error"], line=error["line"])

    def print_parsing_error(self, exception, line):
        self.stdout.write(self.style.ERROR(f"Error: {exception}"))
        self.stdout.write(self.style.ERROR(f"In line: {line}"))
        self.print_dividing_line()

    def print_dividing_line(self):
        self.stdout.write(self.style.ERROR("----------------------------------------------------"))

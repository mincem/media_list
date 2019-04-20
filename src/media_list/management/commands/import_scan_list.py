from django.core.management.base import BaseCommand

from ...utils import ScanListParser


class Command(BaseCommand):
    help = 'Imports manga series from a list of scans'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        results = ScanListParser(options["file"]).perform()
        self.print_parsing_results(results["created"], results["total"])
        self.print_parsing_errors(results["errors"])

    def print_parsing_results(self, created, total):
        self.stdout.write(self.style.SUCCESS(
            f"Finished importing list. Created {created} series from {total} lines."
        ))

    def print_parsing_errors(self, errors):
        if errors:
            self.stdout.write(self.style.ERROR(f"Found {len(errors)} errors:"))
        for error in errors:
            self.stdout.write(self.style.ERROR(error))
            self.stdout.write("------------------------------")

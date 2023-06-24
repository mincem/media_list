from .import_scan_list import Command as ImportScanListCommand
from ...utils.scan_list_parser import OldScanListParser


class Command(ImportScanListCommand):
    help = 'Imports manga series from an old list of scans'

    def handle(self, *_, **options):
        results = OldScanListParser(options["file"], options["source"]).perform()
        self.print_parsing_results(results["created"], results["total"])
        self.print_parsing_errors(results["errors"])

from ...utils import OldScanListParser
from .import_scan_list import Command as ImportScanListCommand


class Command(ImportScanListCommand):
    help = 'Imports manga series from an old list of scans'

    def handle(self, *args, **options):
        results = OldScanListParser(options["file"]).perform()
        self.print_parsing_results(results["created"], results["total"])
        self.print_parsing_errors(results["errors"])

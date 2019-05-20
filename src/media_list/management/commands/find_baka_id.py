from django.core.management.base import BaseCommand

from ...utils import BakaFinder
from ...models import MangaSeries


class Command(BaseCommand):
    help = 'Fetches mangaupdates ID for one or more manga series'

    def add_arguments(self, parser):
        parser.add_argument('series_ids', nargs="+", type=int)

    def handle(self, *args, **options):
        for series_id in options["series_ids"]:
            series = MangaSeries.objects.get(pk=series_id)
            if not series.baka_id:
                series.baka_id = BakaFinder(series.title).baka_id()
                series.save()

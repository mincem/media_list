from django.core.management.base import BaseCommand

from ...utils import BakaParser
from ...models import MediaSeries


class Command(BaseCommand):
    help = 'Imports mangaupdates info for one or more manga series'

    def add_arguments(self, parser):
        parser.add_argument('series_ids', nargs="+", type=int)

    def handle(self, *args, **options):
        for series_id in options["series_ids"]:
            series = MediaSeries.objects.get(pk=series_id)
            if series.baka_id:
                series.baka_info = BakaParser(series.baka_id).perform()
                series.save()

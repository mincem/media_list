from time import sleep

from django.core.management.base import BaseCommand

from ...data_fetchers.baka_sources import fetch_from_sources
from ...models import BakaSeries, MangaKeyword, MangaSeries


class Command(BaseCommand):
    help = 'Fetches Mangaupdates keywords for old BakaSeries models'

    def handle(self, *args, **options):
        for baka_series in BakaSeries.objects.all():
            if baka_series.keywords.count():
                print(f'Series "{baka_series.title}" already has keywords')
            else:
                print(f'Adding keywords to series "{baka_series.title}"... ')
                self.fetch_keywords(baka_series)
                print(f'\rAdded keywords to series "{baka_series.title}"')
                sleep(5)

    def fetch_keywords(self, baka_series):
        result = fetch_from_sources(baka_series.baka_id)
        self.upgrade_id(baka_series, result.baka_id)
        for keyword_data in result.series_data["keywords"]:
            keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
            baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})

    @staticmethod
    def upgrade_id(baka_series, new_id):
        old_id = baka_series.baka_id
        if new_id != old_id:
            baka_series.baka_id = new_id
            baka_series.save()
            MangaSeries.objects.filter(baka_info=baka_series, baka_id=old_id).update(baka_id=new_id)

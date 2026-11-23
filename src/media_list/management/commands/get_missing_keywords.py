from time import sleep

from django.core.management.base import BaseCommand

from ...data_fetchers.external_manga_fetcher import BakaRetriever
from ...models import BakaSeries, MangaKeyword, MangaSeries
from ...serializers.baka_serializer import BakaSerializer
from ...utils import BakaPageScraper


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
        page = BakaRetriever().get(BakaSerializer().url(baka_series))
        self.upgrade_id(baka_series, page.url)
        keywords_data = BakaPageScraper(page_html=page.html, baka_id=baka_series.baka_id).parse()["keywords"]
        for keyword_data in keywords_data:
            keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
            baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})

    @staticmethod
    def upgrade_id(baka_series, final_url):
        old_id = baka_series.baka_id
        new_id = BakaSerializer().upgraded_id(old_id, final_url)
        if new_id != old_id:
            baka_series.baka_id = new_id
            baka_series.save()
            MangaSeries.objects.filter(baka_info=baka_series, baka_id=old_id).update(baka_id=new_id)

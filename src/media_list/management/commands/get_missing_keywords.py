from time import sleep

from django.core.management.base import BaseCommand

from ...data_fetchers.external_manga_fetcher import BakaRetriever
from ...models import BakaSeries, MangaKeyword
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
        keywords_data = BakaPageScraper(
            page_html=BakaRetriever().get(baka_series.baka_id),
            baka_id=baka_series.baka_id,
            baka_code=baka_series.baka_code
        ).parse()["keywords"]
        for keyword_data in keywords_data:
            keyword = MangaKeyword.objects.get_or_create(name=keyword_data["name"])[0]
            baka_series.keywords.add(keyword, through_defaults={"score": keyword_data["score"]})

from google import google
from urllib.parse import urlparse, parse_qs


class BakaFinder:
    def __init__(self, series_title, hardcode=True):
        self.series_title = series_title
        self.hardcode = hardcode

    def baka_id(self):
        link = self.fetch_link()
        url = urlparse(link)
        if self.source_is_correct(url):
            return int(parse_qs(url.query)["id"][0])
        else:
            raise Exception(f"Cannot get Baka-ID from URL: {link}")

    def fetch_link(self):
        if self.hardcode:
            return 'https://www.mangaupdates.com/series.html?id=47446'  # Attack on Titan
        search_results = google.search(f"mangaupdates {self.series_title}")
        return search_results[0].link

    @staticmethod
    def source_is_correct(url):
        return url.hostname == 'www.mangaupdates.com' and url.path == '/series.html'

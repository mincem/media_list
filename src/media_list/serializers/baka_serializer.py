import re
from urllib.parse import urlparse

BASE_URL = "https://www.mangaupdates.com"
CODE_PATH_PATTERN = re.compile(r"/series/(\w+)/?.*")


class BakaSerializer:

    @staticmethod
    def numeric_id_url(baka_id):
        return f"{BASE_URL}/series.html?id={baka_id}"

    @staticmethod
    def alphanumeric_code_url(baka_code):
        return f"{BASE_URL}/series/{baka_code}"

    @staticmethod
    def is_numeric(baka_id):
        return str(baka_id).isdigit()

    @staticmethod
    def code_from_url(url):
        match = CODE_PATH_PATTERN.match(urlparse(url).path)
        return match.group(1) if match else None

    def url(self, manga):
        if not manga.baka_id:
            raise Exception("Missing external item ID")
        if self.is_numeric(manga.baka_id):
            return self.numeric_id_url(manga.baka_id)
        return self.alphanumeric_code_url(manga.baka_id)

    def upgraded_id(self, baka_id, final_url):
        """Return the alphanumeric code if an old numeric ID was redirected to a code URL; otherwise the ID as-is."""
        if baka_id and self.is_numeric(baka_id):
            return self.code_from_url(final_url) or baka_id
        return baka_id

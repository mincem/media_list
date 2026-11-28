import re
from urllib.parse import urlparse

BASE_URL = "https://www.mangaupdates.com"
API_BASE_URL = "https://api.mangaupdates.com/v1"
CODE_PATH_PATTERN = re.compile(r"/series/(\w+)/?.*")
BASE_36_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


class BakaSerializer:

    @staticmethod
    def numeric_id_url(baka_id):
        return f"{BASE_URL}/series.html?id={baka_id}"

    @staticmethod
    def alphanumeric_code_url(baka_code):
        return f"{BASE_URL}/series/{baka_code}"

    @staticmethod
    def api_series_id(baka_code):
        """The API identifies series by the base-36 integer value of the alphanumeric code."""
        return int(baka_code, 36)

    @staticmethod
    def code_from_api_id(api_id):
        """The alphanumeric code for a numeric API ID (the inverse of api_series_id). Works for series and authors."""
        if api_id < 0:
            raise ValueError(f"Mangaupdates API IDs are not negative: {api_id}")
        code = ""
        while True:
            api_id, digit = divmod(api_id, 36)
            code = BASE_36_DIGITS[digit] + code
            if not api_id:
                return code

    @classmethod
    def api_url(cls, baka_code):
        return f"{API_BASE_URL}/series/{cls.api_series_id(baka_code)}"

    @staticmethod
    def is_numeric(baka_id):
        return str(baka_id).isdigit()

    @staticmethod
    def code_from_url(url):
        match = CODE_PATH_PATTERN.match(urlparse(url).path)
        return match.group(1) if match else None

    def url(self, manga):
        return self.url_for_id(manga.baka_id)

    def url_for_id(self, baka_id):
        if not baka_id:
            raise Exception("Missing external item ID")
        if self.is_numeric(baka_id):
            return self.numeric_id_url(baka_id)
        return self.alphanumeric_code_url(baka_id)

    def upgraded_id(self, baka_id, final_url):
        """Return the alphanumeric code if an old numeric ID was redirected to a code URL; otherwise the ID as-is."""
        if baka_id and self.is_numeric(baka_id):
            return self.code_from_url(final_url) or baka_id
        return baka_id

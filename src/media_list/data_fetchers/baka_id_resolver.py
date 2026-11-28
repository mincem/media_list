import logging
from urllib.parse import urljoin

import requests

from .baka_sources import BakaSourceError
from ..id_finders import BakaIDFinder, BakaSearchException, BakaUrlException, LinkFetcher
from ..id_finders.baka_id_finder import BakaSearchRetriever, normalize_title
from ..serializers.baka_serializer import BakaSerializer

logger = logging.getLogger(__name__)

MAX_REDIRECTS = 3


class BakaRedirectReader:
    """Reads where a Mangaupdates URL redirects to, without downloading or following it."""

    @staticmethod
    def location(url):
        with requests.get(url, allow_redirects=False, stream=True, timeout=30) as response:
            if not response.is_redirect:
                return None
            return urljoin(url, response.headers["Location"])


class BakaIDResolutionError(BakaSourceError):
    def __init__(self, baka_id):
        super().__init__(f"Cannot find the current Mangaupdates code for the old ID {baka_id}")


class BakaIDResolver:
    """Resolves a manga's old numeric Mangaupdates ID to its alphanumeric code.

    1. Reads the redirect of the old series.html?id=... URL (www.mangaupdates.com, one request per hop, no page).
    2. If that fails, searches with the API (api.mangaupdates.com):
       - Manga with info: the result whose main title (and year, when both have one) equals the info's. Only an
         exact, unambiguous match is accepted.
       - Manga without info: its numeric ID was never confirmed, so it's found like a manga with no ID (BakaIDFinder,
         with the manga's own title).
    3. If neither gives a code, raises BakaIDResolutionError.
    """

    def __init__(self, redirect_reader=None, search_retriever=None):
        self.redirect_reader = redirect_reader or BakaRedirectReader()
        self.search_retriever = search_retriever or BakaSearchRetriever()

    def resolve(self, manga):
        code = self.code_from_redirect(manga.baka_id) or self.code_from_search(manga)
        if code is None:
            raise BakaIDResolutionError(manga.baka_id)
        return code

    def code_from_redirect(self, numeric_id):
        url = BakaSerializer.numeric_id_url(numeric_id)
        try:
            for _hop in range(MAX_REDIRECTS):
                url = self.redirect_reader.location(url)
                if url is None:
                    return None
                code = BakaSerializer.code_from_url(url)
                if code is not None:
                    return code
        except requests.RequestException as error:
            logger.warning("Cannot read the redirect for Mangaupdates ID %s: %r; searching instead", numeric_id, error)
        return None

    def code_from_search(self, manga):
        if manga.baka_info is not None:
            return self.code_from_info_search(manga.baka_info)
        return self.code_from_title_search(manga.title)

    def code_from_info_search(self, baka_series):
        try:
            results = self.search_retriever.search(baka_series.title)
            matches = [result["record"] for result in results if is_same_series(result["record"], baka_series)]
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            logger.warning('Mangaupdates search failed for "%s": %r', baka_series.title, error)
            return None
        if len(matches) != 1:
            logger.warning('Found %d exact Mangaupdates matches for "%s"', len(matches), baka_series.title)
            return None
        return BakaSerializer.code_from_url(matches[0].get("url") or "")

    def code_from_title_search(self, title):
        try:
            baka_id = BakaIDFinder(title, LinkFetcher(self.search_retriever)).get_id()
        except (requests.RequestException, BakaSearchException, BakaUrlException, ValueError, KeyError) as error:
            logger.warning('Mangaupdates search failed for "%s": %r', title, error)
            return None
        return None if BakaSerializer.is_numeric(baka_id) else baka_id


def is_same_series(record, baka_series):
    """Compares the result's main title (not hit_title, which may be an alternate name) and, if both have it, the year."""
    if normalize_title(record.get("title")) != normalize_title(baka_series.title):
        return False
    record_year = str(record.get("year") or "").strip()
    if record_year and baka_series.year:
        return record_year == str(baka_series.year)
    return True

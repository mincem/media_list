import io
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import requests
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from easy_thumbnails.files import get_thumbnailer
from PIL import Image

from .test_baka_sources import SHINGEKI_CODE, MockBakaApiRetriever, load_sample_json
from .test_external_manga_fetcher import MOCK_BAKA_CODE, MOCK_BAKA_ID, MOCK_REDIRECT_URL, ShingekiMockBakaRetriever
from .test_external_movie_fetcher import MockTMDBClient
from ...data_fetchers import ExternalMangaFetcher, ExternalMovieFetcher
from ...data_fetchers.baka_sources import BakaApiSource, BakaScraperSource, BakaSourceError
from ...models import BakaSeries, IMDBMovie, MangaGenre, MangaKeyword, MangaPerson, MangaSeries, Movie

OTHER_CODE = "b2c3d4e"


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (160, 239), color="red").save(buffer, format="PNG")
    return buffer.getvalue()


class CoverRetriever:
    """Returns a real PNG, so easy_thumbnails can make thumbnails of it."""
    fetched_urls = []

    def __init__(self, image_url):
        self.image_url = image_url

    def fetch(self):
        CoverRetriever.fetched_urls.append(self.image_url)
        return {"name": Path(self.image_url).name, "content": ContentFile(png_bytes())}


class TempMediaMixin:
    """Stores the files the tests save in a temporary MEDIA_ROOT."""

    def setUp(self):
        super().setUp()
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root, ignore_errors=True)
        settings_override = override_settings(MEDIA_ROOT=media_root)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        CoverRetriever.fetched_urls = []


def file_exists(field_file_or_storage, name=None):
    if name is None:
        return field_file_or_storage.storage.exists(field_file_or_storage.name)
    return field_file_or_storage.exists(name)


class MangaRefreshTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.manga = MangaSeries.objects.create(title="Attack on Titan", interest=50, baka_id=SHINGEKI_CODE)

    def fetch(self, series_json=None, manga=None):
        """Fetches from the API sample (or the given series) and runs the on-commit callbacks (file deletion)."""
        manga = manga or self.manga
        retriever = MockBakaApiRetriever(response=series_json)
        with self.captureOnCommitCallbacks(execute=True):
            info = ExternalMangaFetcher(
                item=manga, sources=[BakaApiSource(retriever)], image_retriever_class=CoverRetriever,
            ).fetch()
        manga.refresh_from_db()
        return info

    def test_first_fetch_creates_info(self):
        info = self.fetch()
        self.assertEqual(info, self.manga.baka_info)
        self.assertEqual(SHINGEKI_CODE, info.baka_id)
        self.assertEqual("Shingeki no Kyojin", info.title)

    def test_refresh_updates_info_in_place(self):
        first_info = self.fetch()
        series_json = load_sample_json()
        series_json["title"] = "Attack on Titan"
        series_json["year"] = "2010"
        refreshed_info = self.fetch(series_json)
        self.assertEqual(first_info.pk, refreshed_info.pk)
        self.assertEqual(1, BakaSeries.objects.count())
        self.assertEqual(first_info.pk, self.manga.baka_info_id)
        self.assertEqual("Attack on Titan", refreshed_info.title)
        self.assertEqual(2010, refreshed_info.year)

    def test_refresh_blanks_empty_fields(self):
        self.fetch()
        series_json = load_sample_json()
        series_json.update(
            description=None, status="", year=None, publishers=[], genres=[], authors=[], categories=[],
        )
        info = self.fetch(series_json)
        info.refresh_from_db()
        self.assertEqual("", info.description)
        self.assertEqual("", info.status)
        self.assertIsNone(info.year)
        self.assertEqual("", info.original_publisher)
        self.assertEqual("", info.english_publisher)
        self.assertEqual(0, info.genres.count())
        self.assertEqual(0, info.authors.count())
        self.assertEqual(0, info.artists.count())
        self.assertEqual(0, info.keywords.count())

    def test_refresh_keeps_shared_rows(self):
        self.fetch()
        series_json = load_sample_json()
        series_json.update(genres=[], authors=[], categories=[])
        self.fetch(series_json)
        self.assertTrue(MangaGenre.objects.filter(name="Action").exists())
        self.assertTrue(MangaPerson.objects.filter(name="ISAYAMA Hajime").exists())
        self.assertTrue(MangaKeyword.objects.filter(name="Abandoned Child/ren").exists())

    def test_refresh_replaces_genres_and_people(self):
        self.fetch()
        series_json = load_sample_json()
        series_json["genres"] = [{"genre": "Action"}, {"genre": "Comedy"}]
        series_json["authors"] = [
            {"name": "Someone Else", "type": "Author"},
            {"name": "ISAYAMA Hajime", "type": "Artist"},
        ]
        info = self.fetch(series_json)
        self.assertSetEqual({"Action", "Comedy"}, {str(genre) for genre in info.genres.all()})
        self.assertSetEqual({"Someone Else"}, {str(author) for author in info.authors.all()})
        self.assertSetEqual({"ISAYAMA Hajime"}, {str(artist) for artist in info.artists.all()})

    def test_refresh_updates_keyword_scores(self):
        self.fetch()
        series_json = load_sample_json()
        first_category, second_category = series_json["categories"][:2]
        first_category["votes"] = 999
        series_json["categories"] = [first_category]
        info = self.fetch(series_json)
        scores = {str(keyword): keyword.score for keyword in info.weighed_keywords.all()}
        self.assertDictEqual({first_category["category"]: 999}, scores)
        self.assertTrue(MangaKeyword.objects.filter(name=second_category["category"]).exists())

    def test_refresh_replaces_cover_and_deletes_old_file_and_thumbnails(self):
        info = self.fetch()
        old_image_name, storage = info.image.name, info.image.storage
        thumbnail_name = get_thumbnailer(info.image)["list"].name
        self.assertTrue(file_exists(storage, thumbnail_name))

        refreshed_info = self.fetch()
        self.assertNotEqual(old_image_name, refreshed_info.image.name)
        self.assertTrue(file_exists(refreshed_info.image))
        self.assertFalse(file_exists(storage, old_image_name))
        self.assertFalse(file_exists(storage, thumbnail_name))

    def test_refresh_without_cover_keeps_old_cover(self):
        info = self.fetch()
        old_image_name = info.image.name
        series_json = load_sample_json()
        series_json["image"] = None
        refreshed_info = self.fetch(series_json)
        self.assertEqual(old_image_name, refreshed_info.image.name)
        self.assertTrue(file_exists(refreshed_info.image))

    def test_switching_series_creates_new_info_and_deletes_unused_old_info(self):
        old_info = self.fetch()
        old_image_name, storage = old_info.image.name, old_info.image.storage
        self.manga.baka_id = OTHER_CODE
        new_info = self.fetch()
        self.assertNotEqual(old_info.pk, new_info.pk)
        self.assertEqual(new_info, self.manga.baka_info)
        self.assertEqual(OTHER_CODE, new_info.baka_id)
        self.assertFalse(BakaSeries.objects.filter(pk=old_info.pk).exists())
        self.assertFalse(file_exists(storage, old_image_name))

    def test_switching_series_keeps_old_info_used_by_another_manga(self):
        old_info = self.fetch()
        MangaSeries.objects.create(title="Duplicate", interest=50, baka_id=SHINGEKI_CODE, baka_info=old_info)
        self.manga.baka_id = OTHER_CODE
        self.fetch()
        old_info.refresh_from_db()
        self.assertTrue(file_exists(old_info.image))

    def test_failed_fetch_leaves_manga_and_info_untouched(self):
        info = self.fetch()
        retriever = MockBakaApiRetriever(error=requests.ConnectionError("API down"))
        fetcher = ExternalMangaFetcher(
            item=self.manga, sources=[BakaApiSource(retriever)], image_retriever_class=CoverRetriever,
        )
        with self.assertLogs("media_list.data_fetchers.baka_sources", level="WARNING"):
            with self.assertRaises(BakaSourceError):
                fetcher.fetch()
        self.manga.refresh_from_db()
        info.refresh_from_db()
        self.assertEqual(info, self.manga.baka_info)
        self.assertEqual("Shingeki no Kyojin", info.title)


class OldIdRefreshTests(TempMediaMixin, TestCase):
    """Refreshing info that was fetched with an old numeric ID, through the scraper's redirect."""

    def fetch(self, manga, final_url=None):
        retriever = ShingekiMockBakaRetriever(final_url=final_url)
        with self.captureOnCommitCallbacks(execute=True):
            info = ExternalMangaFetcher(
                item=manga, sources=[BakaScraperSource(retriever)], image_retriever_class=CoverRetriever,
            ).fetch()
        manga.refresh_from_db()
        return info

    def test_redirected_numeric_id_is_refreshed_in_place_and_upgraded_on_both(self):
        manga = MangaSeries.objects.create(title="Attack on Titan", interest=50, baka_id=MOCK_BAKA_ID)
        old_info = self.fetch(manga)
        self.assertEqual(MOCK_BAKA_ID, old_info.baka_id)

        refreshed_info = self.fetch(manga, final_url=MOCK_REDIRECT_URL)
        self.assertEqual(old_info.pk, refreshed_info.pk)
        self.assertEqual(MOCK_BAKA_CODE, manga.baka_id)
        self.assertEqual(MOCK_BAKA_CODE, refreshed_info.baka_id)


class MovieRefreshTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.movie = Movie.objects.create(title="Memento", interest=50, imdb_id=209144)

    def fetch(self):
        with self.captureOnCommitCallbacks(execute=True):
            info = ExternalMovieFetcher(
                self.movie, tmdb_client=MockTMDBClient(), image_retriever_class=CoverRetriever,
            ).fetch()
        self.movie.refresh_from_db()
        return info

    def test_refresh_updates_movie_info_in_place(self):
        first_info = self.fetch()
        cast_count, plot_count = first_info.ordered_cast.count(), first_info.plots.count()
        refreshed_info = self.fetch()
        self.assertEqual(first_info.pk, refreshed_info.pk)
        self.assertEqual(1, IMDBMovie.objects.count())
        self.assertEqual(refreshed_info, self.movie.imdb_info)
        self.assertEqual(cast_count, refreshed_info.ordered_cast.count())
        self.assertEqual(plot_count, refreshed_info.plots.count())


class FetchExternalItemViewTests(TestCase):
    def setUp(self):
        self.manga = MangaSeries.objects.create(title="Attack on Titan", interest=50, baka_id=SHINGEKI_CODE)
        self.url = reverse("categories:manga:get_external_item", kwargs={"pk": self.manga.pk})

    def test_get_is_not_allowed(self):
        with mock.patch("media_list.views.base_views.ExternalItemFetcher.for_item") as for_item:
            response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)
        for_item.assert_not_called()

    def test_post_fetches_and_renders_detail(self):
        with mock.patch("media_list.views.base_views.ExternalItemFetcher.for_item") as for_item:
            response = self.client.post(self.url)
        self.assertEqual(200, response.status_code)
        for_item.return_value.fetch.assert_called_once_with()

    def test_button_says_refresh_when_manga_has_info(self):
        self.manga.baka_info = BakaSeries.objects.create(baka_id=SHINGEKI_CODE, title="Shingeki no Kyojin")
        self.manga.save()
        response = self.client.get(reverse("categories:manga:detail", kwargs={"pk": self.manga.pk}))
        self.assertContains(response, "Refresh from Mangaupdates")

    def test_button_says_get_info_when_manga_has_no_info(self):
        response = self.client.get(reverse("categories:manga:detail", kwargs={"pk": self.manga.pk}))
        self.assertContains(response, "Get Info from Mangaupdates")

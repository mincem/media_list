import json
import re

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...data_fetchers import ExternalItemFetchError, ExternalMangaFetcher
from ...data_fetchers.baka_sources import BakaApiRetriever, BakaApiSource
from ...id_finders.baka_id_finder import normalize_title
from ...integrations import BakaApiParser
from ...models import BakaSeries, MangaSeries
from ...repositories import BakaSeriesRepository
from ...serializers.baka_serializer import BakaSerializer

# Community mapping of every old numeric Mangaupdates ID to its alphanumeric code (a snapshot from January 2023,
# when old IDs were no longer being assigned). Mangaupdates doesn't publish one, and its old series.html?id=... URLs
# now answer 410 Gone instead of redirecting. Downloading it makes no request to Mangaupdates.
MAPPING_URL = "https://raw.githubusercontent.com/henrik9999/mangaupdates-old-id-mapping/main/mapping.json"
CODE_PATTERN = re.compile(r"[0-9a-z]+")
COLUMN_WIDTH = 40


class Command(BaseCommand):
    help = (
        "Converts old numeric Mangaupdates IDs (on manga and on their Mangaupdates info) to alphanumeric codes, "
        "using a mapping of old IDs to codes. Without --review, it makes no requests to Mangaupdates."
    )
    # Replaced in tests
    input_function = input
    api_retriever_class = BakaApiRetriever
    image_retriever_class = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--mapping", metavar="PATH",
            help=f"Local copy of the mapping JSON file (default: download it from {MAPPING_URL})",
        )
        parser.add_argument("--dry-run", action="store_true", help="Show what would change without saving it")
        parser.add_argument(
            "--review", action="store_true",
            help="For each old ID, fetch the series from the Mangaupdates API (one request), show it next to the "
                 "stored data, and convert it only if you accept",
        )
        parser.add_argument(
            "--refresh", action="store_true",
            help="With --review: when you accept, also store the reviewed data as the manga's info (and download "
                 "its cover), like a refresh",
        )

    def handle(self, *args, **options):
        if options["review"] and options["dry_run"]:
            raise CommandError("--dry-run makes no requests, so it can't be combined with --review")
        if options["refresh"] and not options["review"]:
            raise CommandError("--refresh needs --review")
        mapping = self.load_mapping(options["mapping"])
        groups = old_id_groups()
        mapped = {old_id: group for old_id, group in groups.items() if old_id in mapping}
        unmapped = [obj for old_id, group in groups.items() if old_id not in mapping for obj in group.objects()]
        if options["review"]:
            ReviewSession(self, mapping, refresh=options["refresh"]).run(mapped)
        else:
            self.convert_all(mapped, mapping, dry_run=options["dry_run"])
        self.report_unmapped(unmapped)

    def load_mapping(self, path):
        try:
            if path:
                with open(path, encoding="utf-8") as mapping_file:
                    raw_mapping = json.load(mapping_file)
            else:
                self.stdout.write(f"Downloading {MAPPING_URL}")
                response = requests.get(MAPPING_URL, timeout=60)
                response.raise_for_status()
                raw_mapping = response.json()
        except (OSError, ValueError, requests.RequestException) as error:
            raise CommandError(f"Cannot load the mapping: {error}") from error
        return valid_mapping(raw_mapping)

    def convert_all(self, groups, mapping, dry_run):
        with transaction.atomic():
            for old_id, group in groups.items():
                code = mapping[old_id]
                for obj in group.objects():
                    self.stdout.write(
                        f"{label_of(obj)}: {obj.baka_id} -> {code}  {BakaSerializer.alphanumeric_code_url(code)}"
                    )
                group.convert(code)
            if dry_run:
                transaction.set_rollback(True)
        if dry_run:
            self.stdout.write("Dry run: nothing was saved.")

    def report_unmapped(self, unmapped):
        if not unmapped:
            self.stdout.write(self.style.SUCCESS("Every numeric ID is in the mapping."))
            return
        self.stdout.write(self.style.WARNING(f"{len(unmapped)} numeric IDs are not in the mapping and were kept:"))
        for obj in unmapped:
            self.stdout.write(f"  {label_of(obj)}: {obj.baka_id}")


class OldIdGroup:
    """The manga and the Mangaupdates info that share one old numeric ID."""

    def __init__(self):
        self.manga = []
        self.infos = []

    def objects(self):
        return self.manga + self.infos

    def reference_info(self):
        """The stored info to compare the fetched series against, if there's any."""
        if self.infos:
            return self.infos[0]
        return next((manga.baka_info for manga in self.manga if manga.baka_info is not None), None)

    def convert(self, code):
        for obj in self.objects():
            obj.baka_id = code
            obj.save(update_fields=["baka_id"])


def old_id_groups():
    """Groups every manga and info that has a numeric ID by that ID (normalized, so "047" and "47" are the same)."""
    groups = {}
    for model, attribute in ((MangaSeries, "manga"), (BakaSeries, "infos")):
        for obj in model.objects.exclude(baka_id__isnull=True).exclude(baka_id="").order_by("pk"):
            old_id = str(obj.baka_id).strip()
            if BakaSerializer.is_numeric(old_id):
                getattr(groups.setdefault(str(int(old_id)), OldIdGroup()), attribute).append(obj)
    return dict(sorted(groups.items(), key=lambda item: int(item[0])))


class FixedApiRetriever:
    """Serves the series data that was already fetched for the review, so a refresh doesn't request it again."""

    def __init__(self, series_json):
        self.series_json = series_json

    def get(self, _baka_code):
        return self.series_json


class ReviewSession:
    def __init__(self, command, mapping, refresh):
        self.command = command
        self.stdout = command.stdout
        self.style = command.style
        self.mapping = mapping
        self.refresh = refresh
        self.api_retriever = command.api_retriever_class()
        self.counts = {"accepted": 0, "skipped": 0, "refresh failed": 0}

    def run(self, groups):
        total = len(groups)
        for position, (old_id, group) in enumerate(groups.items(), start=1):
            if not self.review(position, total, old_id, group):
                self.stdout.write("Stopped. Accepted IDs are already saved; the rest are still numeric.")
                break
        self.stdout.write(", ".join(f"{count} {name}" for name, count in self.counts.items()))

    def review(self, position, total, old_id, group):
        """Reviews one old ID. Returns False if the user quit."""
        code = self.mapping[old_id]
        self.stdout.write("")
        self.stdout.write(f"[{position}/{total}] {old_id} -> {code}  {BakaSerializer.alphanumeric_code_url(code)}")
        for obj in group.objects():
            self.stdout.write(f"  {label_of(obj)}")
        series_json, answer = self.fetch(code)
        if series_json is None:
            if answer == "q":
                return False
            self.counts["skipped"] += 1
            return True
        self.show_comparison(group, series_json, code)
        answer = self.ask("[Enter] accept   [s] skip   [q] quit: ", {"", "s", "q"})
        if answer == "q":
            return False
        if answer == "s":
            self.counts["skipped"] += 1
            return True
        self.accept(group, code, series_json)
        return True

    def fetch(self, code):
        """Fetches the series, asking before any retry. Returns (series_json, None), or (None, "s" or "q")."""
        while True:
            try:
                return self.api_retriever.get(code), None
            except (requests.RequestException, ValueError) as error:
                self.stdout.write(self.style.ERROR(f"  Cannot fetch {code}: {error}"))
                answer = self.ask("[r] retry   [s] skip   [q] quit: ", {"r", "s", "q"})
                if answer != "r":
                    return None, answer

    def show_comparison(self, group, series_json, code):
        fetched = BakaApiParser(series_json, baka_id=code).parse()
        alternate_titles = [entry.get("title") for entry in series_json.get("associated") or []]
        info = group.reference_info()
        if info is not None:
            stored_title, stored_year = info.title, info.year
            stored_people = {str(person) for person in [*info.authors.all(), *info.artists.all()]}
        else:
            stored_title, stored_year, stored_people = group.manga[0].title, None, set()
        fetched_people = {person["name"] for person in [*fetched["authors"], *fetched["artists"]]}
        rows = [
            ("", "stored" if info is not None else "manga (no info)", "Mangaupdates"),
            ("title", stored_title, fetched["title"]),
            ("year", stored_year, fetched["year"]),
            ("authors", ", ".join(sorted(stored_people)), ", ".join(sorted(fetched_people))),
        ]
        for name, stored, new in rows:
            self.stdout.write(f"  {name:<8} {cell(stored):<{COLUMN_WIDTH}} {cell(new)}")
        verdict = match_verdict(
            {"title": stored_title, "year": stored_year, "people": stored_people},
            {"title": fetched["title"], "alternate_titles": alternate_titles, "year": fetched["year"],
             "people": fetched_people},
        )
        style = self.style.SUCCESS if verdict.startswith("MATCH") else self.style.WARNING
        self.stdout.write(f"  {'verdict':<8} {style(verdict)}")

    def accept(self, group, code, series_json):
        with transaction.atomic():
            group.convert(code)
        self.counts["accepted"] += 1
        self.stdout.write(self.style.SUCCESS(f"  Converted to {code}"))
        if self.refresh and group.manga:
            self.refresh_info(group, series_json)

    def refresh_info(self, group, series_json):
        """Stores the reviewed data as the info of the group's manga, then points the rest of them at the same info.

        The ID conversion is already saved, so if this fails, the manga can still be refreshed later from its page.
        """
        # Reloaded, so no info cached before the conversion (with the old ID) is compared against the new code
        all_manga = list(MangaSeries.objects.filter(pk__in=[manga.pk for manga in group.manga]).order_by("pk"))
        main_manga = next((manga for manga in all_manga if manga.baka_info is not None), all_manga[0])
        try:
            fetcher = ExternalMangaFetcher(
                main_manga,
                sources=[BakaApiSource(FixedApiRetriever(series_json))],
                image_retriever_class=self.command.image_retriever_class,
            )
            info = fetcher.fetch()
            for manga in all_manga:
                if manga.pk != main_manga.pk:
                    point_at_info(manga, info)
        except (ExternalItemFetchError, requests.RequestException, OSError) as error:
            self.counts["refresh failed"] += 1
            self.stdout.write(self.style.ERROR(f"  Refresh failed ({error}); the ID is converted anyway"))
            return
        self.stdout.write(self.style.SUCCESS(f"  Refreshed info: {info.title}"))

    def ask(self, prompt, valid_answers):
        while True:
            answer = self.command.input_function(prompt).strip().lower()
            if answer in valid_answers:
                return answer


def point_at_info(manga, info):
    """Points the manga at the info, deleting its old info if nothing else uses it (e.g. duplicates of one series)."""
    with transaction.atomic():
        old_info = manga.baka_info
        manga.baka_info = info
        manga.save()
        if old_info is not None and old_info.pk != info.pk and not old_info.mangaseries_set.exists():
            BakaSeriesRepository.delete(old_info)


def match_verdict(stored, fetched):
    """Summarizes how well the fetched series matches the stored data, for the user to decide.

    `stored` has a title, year and people (authors and artists); `fetched` also has alternate_titles.
    """
    wanted = normalize_title(stored["title"])
    signals = []
    if wanted == normalize_title(fetched["title"]):
        signals.append("title")
    elif wanted in {normalize_title(alternate) for alternate in fetched["alternate_titles"]}:
        signals.append("alternate title")
    if stored["year"] and fetched["year"] and int(stored["year"]) == int(fetched["year"]):
        signals.append("year")
    if stored["people"] & fetched["people"]:
        signals.append("author")
    if "title" in signals:
        return f"MATCH ({', '.join(signals)})"
    if signals:
        return f"PARTIAL ({', '.join(signals)})"
    return "NO MATCH"


def cell(value):
    text = "-" if value in (None, "") else str(value)
    return text if len(text) <= COLUMN_WIDTH else text[:COLUMN_WIDTH - 1] + "…"


def label_of(obj):
    kind = "Manga" if isinstance(obj, MangaSeries) else "Info"
    return f"{kind} #{obj.pk} {obj.title!r}"


def valid_mapping(raw_mapping):
    """Keeps only numeric keys mapped to codes, and refuses a mapping that sends two old IDs to the same code."""
    if not isinstance(raw_mapping, dict):
        raise CommandError("The mapping must be a JSON object of old IDs to codes")
    mapping = {
        str(int(old_id)): code
        for old_id, code in raw_mapping.items()
        if str(old_id).isdigit() and isinstance(code, str) and CODE_PATTERN.fullmatch(code) and not code.isdigit()
    }
    if len(set(mapping.values())) != len(mapping):
        raise CommandError("The mapping sends more than one old ID to the same code")
    return mapping

import re

from ..models import MangaSeries
from ..serializers.manga_serializers import MangaSerializer


def process_links(links):
    """Parses each {"text", "url"} link and serializes its matches, keeping the order of the links."""
    entries = [parse_entry(text=link["text"], url=link["url"]) for link in links]
    for entry in entries:
        entry["matches"] = [MangaSerializer(match).data for match in entry["matches"]]
    return entries


ENTRY_PATTERN = re.compile(r"\s*(\S.*?)(?: (?:v\d+-)?v?(\d+)|\s*[\[\(\{]|$).*")


def parse_entry(text, url):
    """Splits link text into title and volume count. The title ends before a volume number or a bracket;
    without either, the whole text is the title. Blank text gives an empty title and no matches."""
    match = re.match(ENTRY_PATTERN, text)
    title = match.group(1).strip() if match else ""
    return {
        "full_text": text,
        "matched_text": match.group(0) if match else "",
        "link": url,
        "title": title,
        "volumes": int(match.group(2)) if match and match.group(2) else 0,
        "matches": manga_matches(title) if title else MangaSeries.objects.none()
    }


def manga_matches(title):
    prefix = title[:10]
    query = MangaSeries.objects.filter(title__icontains=prefix) | \
            MangaSeries.objects.filter(alternate_title__icontains=prefix)
    return query.all()

import re

from ..models import MangaSeries
from ..serializers.manga_serializers import MangaSerializer


def process_markdown(markdown):
    entries = entries_in_line(markdown)
    for entry in entries:
        entry["matches"] = [MangaSerializer(match).data for match in entry["matches"]]
    return entries


def entries_in_line(line):
    markdown_link_pattern = re.compile(r"\[([\w\W \t\d]+?)\]\(((?:/|https?://)[\w\W \t\d./?=#]+?)\)")
    matches = re.finditer(markdown_link_pattern, line)
    return [parse_entry(text=match.group(1), url=match.group(2)) for match in matches]


def parse_entry(text, url):
    pattern = re.compile(r"(\w.*?)(?: (?:v\d+-)?v?([\d]+)| [\[\(\{]).*")

    match = re.match(pattern, text)
    if match is None:
        return None
    title = match.group(1).strip()
    if not title:
        return None
    return {
        "full_text": text,
        "matched_text": match.group(0),
        "link": url,
        "title": title,
        "volumes": int(match.group(2)) if match.group(2) else 0,
        "matches": manga_matches(title)
    }


def manga_matches(title):
    prefix = title[:10]
    print(prefix)
    query = MangaSeries.objects.filter(title__icontains=prefix) | \
            MangaSeries.objects.filter(alternate_title__icontains=prefix)
    return query.all()

import re

from ..models import MangaSeries


def matches_in_line(line):
    markdown_link_pattern = re.compile(r"\[([\w\W\s\d]+?)\]\(((?:/|https?://)[\w\W\s\d./?=#]+)\)")
    return [{"text": match.group(1), "url": match.group(2)} for match in re.finditer(markdown_link_pattern, line)]


def parse_entry(text, url):
    pattern = re.compile(r"(.*?)\(?[ v[\d]+-?v?([\d]+)]?")
    match = re.match(pattern, text)
    if match is None:
        return None
    title = match.group(1).strip()
    if not title:
        return None
    return {
        "full_text": match.group(0),
        "link": url,
        "title": title,
        "volumes": int(match.group(2)) if match.group(2) else 0,
        "matches": manga_matches(title)
    }


def manga_matches(title):
    query = MangaSeries.objects.filter(title__icontains=title) | \
            MangaSeries.objects.filter(alternate_title__icontains=title)
    return query.all()

class BakaApiParser:
    """Maps a Mangaupdates API series response to the same data shape BakaPageScraper produces."""

    def __init__(self, series_json, baka_id=None):
        self.baka_id = baka_id
        self.series = series_json

    def parse(self):
        return {
            "baka_id": self.baka_id or None,
            "title": self.series["title"],
            "genre_names": [genre["genre"] for genre in self.series.get("genres") or []],
            "keywords": self.parse_keywords(),
            "description": self.series.get("description") or "",
            "status": self.series.get("status") or "",
            "author_names": self.parse_people(person_type="Author"),
            "artist_names": self.parse_people(person_type="Artist"),
            "year": self.parse_year(),
            "original_publisher": self.parse_publishers(publisher_type="Original"),
            "english_publisher": self.parse_publishers(publisher_type="English"),
            "image_url": self.parse_image_url(),
        }

    def parse_keywords(self):
        return [
            {"name": category["category"], "score": category["votes"]}
            for category in self.series.get("categories") or []
        ]

    def parse_people(self, person_type):
        return [person["name"] for person in self.series.get("authors") or [] if person["type"] == person_type]

    def parse_year(self):
        year = str(self.series.get("year") or "").strip()
        return int(year) if year.isdigit() else None

    def parse_publishers(self, publisher_type):
        return ", ".join(
            publisher_label(publisher)
            for publisher in self.series.get("publishers") or []
            if publisher["type"] == publisher_type
        )

    def parse_image_url(self):
        image = self.series.get("image") or {}
        return (image.get("url") or {}).get("original") or None


def publisher_label(publisher):
    name = publisher["publisher_name"]
    notes = publisher.get("notes")
    return f"{name} ({notes})" if notes else name

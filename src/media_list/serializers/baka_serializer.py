class BakaSerializer:

    @staticmethod
    def numeric_id_url(baka_id):
        return f"https://www.mangaupdates.com/series.html?id={baka_id}"

    @staticmethod
    def alphanumeric_code_url(baka_code):
        return f"https://www.mangaupdates.com/series/{baka_code}"

    def url(self, manga):
        if manga.baka_code:
            return self.alphanumeric_code_url(manga.baka_code)
        if manga.baka_id:
            return self.numeric_id_url(manga.baka_id)
        raise Exception("Missing external item ID")

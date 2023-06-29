class BakaSerializer:

    @staticmethod
    def numeric_id_url(baka_id):
        return f"https://www.mangaupdates.com/series.html?id={baka_id}"

    @staticmethod
    def alphanumeric_code_url(baka_code):
        return f"https://www.mangaupdates.com/series/{baka_code}"

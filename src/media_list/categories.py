from dataclasses import make_dataclass

__all__ = ["all_categories", "manga_category", "movie_category"]

Category = make_dataclass("Category", ["verbose_name", "verbose_name_plural", "path"])

manga_category = Category(
    verbose_name="manga",
    verbose_name_plural="manga",
    path="manga",
)

movie_category = Category(
    verbose_name="movie",
    verbose_name_plural="movies",
    path="movie",
)


def all_categories():
    return [
        manga_category,
        movie_category,
    ]

from dataclasses import dataclass

__all__ = ["all_categories", "manga_category", "movie_category"]


@dataclass
class Category:
    verbose_name: str
    verbose_name_plural: str
    path: str


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

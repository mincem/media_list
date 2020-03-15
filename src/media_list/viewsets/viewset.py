from dataclasses import dataclass
from typing import Any

from django.views import generic


@dataclass
class Viewset:
    list_view: Any = generic.View
    grid_view: Any = generic.View
    detail_view: Any = generic.View
    create_view: Any = generic.View
    edit_view: Any = generic.View
    edit_interest_view: Any = generic.View
    edit_title_view: Any = generic.View
    edit_alternate_title_view: Any = generic.View
    delete_view: Any = generic.View
    find_external_id_view: Any = generic.View
    find_external_data_view: Any = generic.View
    swap_titles_view: Any = generic.View

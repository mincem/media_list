from django.urls import path, include

from . import viewsets
from .views import base_views


def category_urls(viewset):
    return [
        path('', viewset.list_view.as_view(), name='list'),
        path('<int:pk>/', viewset.list_view.as_view(), name='list'),
        path('grid/', viewset.grid_view.as_view(), name='grid'),
        path('<int:pk>/detail/', viewset.detail_view.as_view(), name='detail'),

        path('create/', viewset.create_view.as_view(), name='create'),
        path('<int:pk>/edit/', viewset.edit_view.as_view(), name='edit'),
        path('<int:pk>/edit_interest/', viewset.edit_interest_view.as_view(), name='edit_interest'),
        path('<int:pk>/edit_title/', viewset.edit_title_view.as_view(), name='edit_title'),
        path('<int:pk>/edit_alternate_title/', viewset.edit_alternate_title_view.as_view(),
             name='edit_alternate_title'),
        path('<int:pk>/delete/', viewset.delete_view.as_view(), name='delete'),

        path('<int:pk>/get_external_id/', viewset.find_external_id_view.as_view(), name='get_external_id'),
        path('<int:pk>/get_external_item/', viewset.find_external_data_view.as_view(), name='get_external_item'),
        path('<int:pk>/swap_titles/', viewset.swap_titles_view.as_view(), name='swap_titles'),
    ]


categories_urls = [
    path('manga/', include((category_urls(viewsets.manga_viewset), 'manga'))),
    path('movie/', include((category_urls(viewsets.movie_viewset), 'movie'))),
]

urlpatterns = [
    path('categories/', include((categories_urls, 'categories'), namespace='categories')),
    path('', base_views.LandingView.as_view(), name='landing'),
]

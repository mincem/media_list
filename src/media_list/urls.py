from django.urls import path, include
from django.views import generic

from . import views

manga_urls = [
    path('', views.MangaListView.as_view(), name='list'),
    path('<int:pk>/', views.MangaListView.as_view(), name='list'),
    path('grid/', views.MangaGridView.as_view(), name='grid'),
    path('<int:pk>/detail/', views.MangaDetailView.as_view(), name='detail'),

    path('create/', views.MangaCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.MangaEditView.as_view(), name='edit'),
    path('<int:pk>/edit_interest/', views.MangaEditInterestView.as_view(), name='edit_interest'),
    path('<int:pk>/delete/', views.MangaDeleteView.as_view(), name='delete'),

    path('<int:pk>/get_baka_id/', views.MangaFetchBakaIDView.as_view(), name='get_baka_id'),
    path('<int:pk>/get_baka_info/', views.MangaFetchBakaInfoView.as_view(), name='get_baka_info'),
    path('<int:pk>/swap_titles/', views.MangaSwapTitlesView.as_view(), name='swap_titles'),
]

movie_urls = [
    path('', views.MovieListView.as_view(), name='list'),
    path('<int:pk>/', views.MovieListView.as_view(), name='list'),
    path('grid/', views.MovieGridView.as_view(), name='grid'),
    path('<int:pk>/detail/', views.MovieDetailView.as_view(), name='detail'),

    path('create/', views.MovieCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.MovieEditView.as_view(), name='edit'),
    path('<int:pk>/edit_interest/', views.MovieEditInterestView.as_view(), name='edit_interest'),
    path('<int:pk>/delete/', views.MovieDeleteView.as_view(), name='delete'),

    path('<int:pk>/swap_titles/', generic.View.as_view(), name='swap_titles'),
]

categories_urls = [
    path('manga/', include((manga_urls, 'manga'))),
    path('movie/', include((movie_urls, 'movie'))),
]

urlpatterns = [
    path('categories/', include((categories_urls, 'categories'), namespace='categories')),
    path('', views.LandingView.as_view(), name='landing'),
]

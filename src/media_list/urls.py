from django.urls import path, include

from . import views

manga_urls = [
    path('', views.IndexView.as_view(), name='index'),
    path('grid/', views.GridView.as_view(), name='grid'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('<int:pk>/', views.IndexView.as_view(), name='index_and_modal'),
    path('<int:pk>/detail/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditView.as_view(), name='edit'),
    path('<int:pk>/edit_interest/', views.EditInterestView.as_view(), name='edit_interest'),
    path('<int:pk>/delete/', views.DeleteView.as_view(), name='delete'),
    path('<int:pk>/get_baka_id/', views.FetchBakaIDView.as_view(), name='get_baka_id'),
    path('<int:pk>/get_baka_info/', views.FetchBakaInfoView.as_view(), name='get_baka_info'),
    path('<int:pk>/swap_titles/', views.SwapMangaSeriesTitlesView.as_view(), name='swap_titles'),
]

categories_urls = [
    path('manga/', include((manga_urls, 'manga'))),
]

urlpatterns = [
    path('categories/', include((categories_urls, 'categories'), namespace='categories')),
    path('', views.LandingView.as_view(), name='landing'),
]

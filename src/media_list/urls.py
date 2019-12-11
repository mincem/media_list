from django.urls import path, include

from . import views

manga_urls = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.IndexView.as_view(), name='index_and_modal'),
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', views.EditView.as_view(), name='edit'),
    path('edit_interest/<int:pk>/', views.EditInterestView.as_view(), name='edit_interest'),
    path('delete/<int:pk>/', views.DeleteView.as_view(), name='delete'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('get_baka_id/<int:pk>/', views.FetchBakaIDView.as_view(), name='get_baka_id'),
    path('get_baka_info/<int:pk>/', views.FetchBakaInfoView.as_view(), name='get_baka_info'),
    path('swap_titles/<int:pk>/', views.SwapMangaSeriesTitlesView.as_view(), name='swap_titles'),
]

urlpatterns = [
    path('manga/', include((manga_urls, 'manga'))),
]

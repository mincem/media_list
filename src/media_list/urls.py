from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # ex: media_list/detail/5/
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', views.EditView.as_view(), name='edit'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('get_baka_id/<int:pk>/', views.FetchBakaIDView.as_view(), name='get_baka_id'),
    path('get_baka_info/<int:pk>/', views.FetchBakaInfoView.as_view(), name='get_baka_info'),
    path('magic/', views.MagicView.as_view(), name='magic'),
]

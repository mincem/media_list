from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # ex: media_list/detail/5/
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('magic/', views.MagicView.as_view(), name='magic'),
]

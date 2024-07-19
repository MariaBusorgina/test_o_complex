from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('weather/<str:city_name>/', views.weather_detail, name='weather_detail'),
    path('city-search-count/', views.city_search_count_api, name='city_search_count_api'),
    path('search-history/', views.search_history, name='search_history'),
    path('city-autocomplete/', views.city_autocomplete, name='city_autocomplete'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Make the landing page the main page
    path('spotify_login/', views.spotify_login, name='spotify_login'),
    path('spotify_callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify_profile/', views.spotify_profile, name='spotify_profile'),
]

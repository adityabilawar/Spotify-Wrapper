from django.urls import path
from . import views
from django.views.i18n import set_language

urlpatterns = [
    path('', views.home_view, name='home'),  # Make the landing page the main page
    path('spotify_login/', views.spotify_login, name='spotify_login'),
    path('spotify_callback/', views.spotify_callback, name='spotify_callback'),
    # path('spotify_profile/', views.spotify_profile, name='spotify_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact'),
    path('landing/', views.landing_page, name='landing_page'),
    path('generate_wrap/', views.generate_wrap, name='generate_wrap'),
    path('wrap/<int:wrap_id>/', views.view_wrap, name='view_wrap'), #temp
    path('delete_all_wraps/', views.delete_all_wraps, name='delete_all_wraps'),
    path('es/landing/', views.landing_page_es, name='landing_page_es'),  # Spanish
    path('fr/landing/', views.landing_page_fr, name='landing_page_fr'),
    path('en/landing/', views.landing_page, name='landing_page'),
    path('set_language/', set_language, name='set_language'),
    path('create_duo_message/', views.create_duo_message, name='create_duo_message'),
    path('generate_duo_wrap/', views.generate_duo_wrap, name='generate_duo_wrap'),
    path('duo_wrap/<int:duowrap_id>/', views.view_duo_wrap, name='view_duo_wrap'),
]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date

def home_view(request):
    return render(request, 'base.html')

def user_data_view(request):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                   client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                                                   redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                                                   scope="user-top-read"))
    results = sp.current_user_top_tracks()
    return render(request, 'slides.html', {'tracks': results['items']})

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def holiday_wrapped_view(request):
    holidays = {
        "Halloween": (10, 31),
        "Christmas": (12, 25),
    }
    today = date.today()
    if any(today.month == m and today.day == d for _, (m, d) in holidays.items()):
        # Custom logic for a holiday-specific wrap
        pass
    return render(request, 'slides.html')

def contact_view(request):
    return render(request, 'contact.html')

import os
from django.shortcuts import render, redirect
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def home_view(request):
    return render(request, 'base.html')


# Spotify authentication and data fetching
def get_spotify_auth():
    return SpotifyOAuth(client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                        scope="user-top-read")


@login_required
def user_data_view(request):
    sp_oauth = get_spotify_auth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        # If not authenticated, redirect to Spotify login
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    sp = Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=10)  # Get user's top tracks
    return render(request, 'slides.html', {'tracks': top_tracks['items']})


# Callback to handle the Spotify OAuth
def callback_view(request):
    sp_oauth = get_spotify_auth()
    token_info = sp_oauth.get_access_token(request.GET['code'])

    # Save the token for future use
    request.session['token_info'] = token_info
    return redirect('user_data')


# Duo Wrapped view
@login_required
def duo_wrapped_view(request):
    sp_oauth = get_spotify_auth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        return redirect(sp_oauth.get_authorize_url())

    sp = Spotify(auth=token_info['access_token'])

    # Fetch user and friend's data (simulating friend's data)
    top_tracks_user = sp.current_user_top_tracks(limit=10)
    top_tracks_friend = sp.current_user_top_tracks(limit=10, offset=10)

    # Combine data
    duo_tracks = list(zip(top_tracks_user['items'], top_tracks_friend['items']))
    return render(request, 'duo_wrapped.html', {'duo_tracks': duo_tracks})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to user's dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            login(request, user)  # Automatically log the user in after registration
            return redirect('dashboard')
        else:
            return render(request, 'register.html', {'error': 'Username already exists'})
    return render(request, 'register.html')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

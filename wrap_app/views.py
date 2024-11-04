import os
import requests
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from django.core.cache import cache

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1/me'


def home_view(request):
    """Renders the home page."""
    return render(request, 'home.html')


def spotify_login(request):
    """Initiates the Spotify OAuth flow by redirecting the user to the authorization page."""
    scopes = 'user-read-private user-read-email user-top-read'
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scopes}"
    return redirect(auth_url)


def spotify_callback(request):
    """Handles the callback from Spotify and exchanges the authorization code for an access token."""
    code = request.GET.get('code')

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    # Save the access token in the session
    access_token = token_json.get('access_token')
    request.session['spotify_access_token'] = access_token

    return redirect('spotify_profile')


def spotify_profile(request):
    """Fetches the user's Spotify profile information using the access token."""
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    profile_response = requests.get(SPOTIFY_API_URL, headers=headers)
    profile_data = profile_response.json()
    profile_data["product"] = profile_data["product"][0].upper() + profile_data["product"][1:]
    top_song = get_top_song(access_token) if access_token else None
    top_artists = get_top_artists(access_token) if access_token else None
    context = {
        'user_profile': profile_data,
        'top_song': top_song,
        'top_artists': top_artists,
    }
    return render(request, 'spotify_profile.html', context)

def get_top_song(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    url = 'https://api.spotify.com/v1/me/top/tracks?limit=1'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            top_track = data['items'][0]  # Get the top track (most listened to)
            return {
                'title': top_track['name'],
                'artist': top_track['artists'][0]['name'],
                'album': top_track['album']['name'],
                'popularity': top_track['popularity'],
                'image_url': top_track['album']['images'][0]['url'],
                'preview_url': top_track['preview_url']
            }
    return None


def logout_view(request):
    """Logs the user out by clearing the session and cache token."""
    # Remove token from session if it's there
    if 'spotify_access_token' in request.session:
        del request.session['spotify_access_token']

    # Clear cache for any token-specific key if applicable
    cache_key = f"spotify_token_{request.user.id}"  # Adjust cache key if needed
    cache.delete(cache_key)

    # Flush the session
    request.session.flush()

    # Redirect to the home page
    return redirect('home')

def get_top_artists(access_token, limit=3):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    url = f'https://api.spotify.com/v1/me/top/artists?limit={limit}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        artists = []
        for artist in data['items']:
            artists.append({
                'name': artist['name'],
                'genre': artist['genres'][0] if artist['genres'] else "Unknown Genre",
                'image_url': artist['images'][0]['url'] if artist['images'] else None
            })
        return artists
    return []
import os
import requests
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from django.core.cache import cache
import google.generativeai as genai
from .models import Wrap
from datetime import datetime
from django.utils.timezone import now
from django.contrib.auth.models import User
import json
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
GEMINI_KEY = os.getenv('GEMINI_KEY')

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1/me'

def home_view(request):
    """Renders the home page."""
    return render(request, 'home.html')

def landing_page(request):
    access_token = request.session.get('spotify_access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    profile_response = requests.get(SPOTIFY_API_URL, headers=headers)
    if profile_response.status_code == 200:
        all_wraps = Wrap.objects.all()  # Retrieve previous wraps
        previous_wraps = []
        for wrap in all_wraps:
            if wrap.spotify_username == profile_response.json().get("display_name", "Unknown"):
                previous_wraps.append(wrap)
        return render(request, 'landing.html', {'previous_wraps': previous_wraps if previous_wraps else None})
    return render(request, 'error.html')

def generate_wrap(request):
    """Fetches the user's Spotify profile information and stores it in the database."""
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    profile_response = requests.get(SPOTIFY_API_URL, headers=headers)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        spotify_username = profile_data.get("display_name", "Unknown")
        product = profile_data.get("product", "Unknown").capitalize()

        # Fetch additional data
        top_song = get_top_song(access_token)
        top_artists = get_top_artists(access_token, limit=3)
        listened_genre = get_most_listened_genre(access_token)
        top_album = get_top_album(access_token)
        listened_hours = get_listened_hours(access_token)
        most_listened_artist = get_most_listened_artist(access_token)
        top_artist_tracks = None
        if most_listened_artist:
            top_artist_tracks = get_top_tracks_for_artist(access_token, most_listened_artist['id'])

        top_artist_song = get_top_artist_song(access_token, top_artists[0] if top_artists else None)
        special_message = "Thank you for being a loyal listener!"
        gemini_recommendations = get_recommendations_from_gemini(top_song, top_artists)

        # Save data to the database
        wrap = Wrap.objects.create(
            spotify_username=spotify_username,
            product=product,
            top_song=top_song,
            top_artists=top_artists,
            listened_genre=listened_genre,
            top_album=top_album,
            listened_hours=listened_hours,
            most_listened_artist=most_listened_artist,
            top_artist_tracks=top_artist_tracks,
            top_artist_song=top_artist_song,
            special_message=special_message,
            gemini_recommendations=gemini_recommendations,
            created_at=now()
        )
        wrap.save()

        # Return a success response (optional)
        return redirect('wrap_success')  # Redirect to a success page or endpoint
    else:
        return render(request, 'error.html', {'message': 'Failed to retrieve Spotify profile information.'})

def spotify_login(request):
    """Initiates the Spotify OAuth flow by redirecting the user to the authorization page."""
    scopes = 'user-read-private user-read-email user-top-read'
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scopes}&show_dialog=true"
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

    if token_response.status_code == 200:
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if access_token:
            # Store the access token in the session
            request.session['spotify_access_token'] = access_token
            return redirect('landing_page')
        else:
            return redirect('home')
    else:
        return redirect('home')

def spotify_profile(request):
    """Fetches the user's Spotify profile information using the access token."""
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        return redirect('spotify_login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    profile_response = requests.get(SPOTIFY_API_URL, headers=headers)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        profile_data["product"] = profile_data.get("product", "Unknown").capitalize()

        # Fetch additional data
        top_song = get_top_song(access_token)
        top_artists = get_top_artists(access_token, limit=3)
        listened_genre = get_most_listened_genre(access_token)
        top_album = get_top_album(access_token)
        listened_hours = get_listened_hours(access_token)
        most_listened_artist = get_most_listened_artist(access_token)
        top_artist_tracks = None
        if most_listened_artist:
            top_artist_tracks = get_top_tracks_for_artist(access_token, most_listened_artist['id'])

        top_artist_song = get_top_artist_song(access_token, top_artists[0] if top_artists else None)
        special_message = "Thank you for being a loyal listener!"
        gemini_recommendations = get_recommendations_from_gemini(top_song, top_artists)

        context = {
            'user_profile': profile_data,
            'top_song': top_song,
            'top_artists': top_artists,
            'listened_genre': listened_genre,
            'top_album': top_album,
            'listened_hours': listened_hours,
            'top_artist_song': top_artist_song,
            'special_message': special_message,
            'gemini_recommendations': gemini_recommendations,
            'top_artist_tracks': top_artist_tracks,
        }
        return render(request, 'spotify_profile.html', context)
    else:
        return render(request, 'error.html', {'message': 'Failed to retrieve Spotify profile information.'})

def get_top_song(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/top/tracks?limit=1'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            top_track = data['items'][0]
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
    if 'spotify_access_token' in request.session:
        del request.session['spotify_access_token']

    cache_key = f"spotify_token_{request.user.id}"
    cache.delete(cache_key)
    request.session.flush()
    return redirect('home')

def get_top_artists(access_token, limit=3):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.spotify.com/v1/me/top/artists?limit={limit}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        artists = []
        for artist in data['items']:
            genre = artist['genres'][0] if artist['genres'] else "Unknown Genre"
            if genre != "Unknown Genre":
                genre = ' '.join(word.capitalize() for word in genre.split())
            artists.append({
                'name': artist['name'],
                'genre': genre,
                'image_url': artist['images'][0]['url'] if artist['images'] else None
            })
        return artists
    return []

def contact_view(request):
    """Renders the contact page."""
    return render(request, 'contact.html')

def get_most_listened_genre(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/top/artists?limit=10'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        genres = [' '.join(word.capitalize() for word in genre.split()) for artist in data['items'] for genre in artist['genres']]
        return max(set(genres), key=genres.count) if genres else "Unknown Genre"
    return "Unknown Genre"

def get_top_album(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/top/tracks?limit=10'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        albums = [track['album'] for track in data['items']]
        for album in albums:
            album['popularity'] = album.get('popularity', 0)
        top_album = max(albums, key=lambda album: album['popularity'])
        return {
            'name': top_album['name'],
            'artist': top_album['artists'][0]['name'],
            'image_url': top_album['images'][0]['url'] if top_album['images'] else None
        }
    return None

def get_listened_hours(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        total_ms = sum(item['track']['duration_ms'] for item in data['items'])
        return round(total_ms / (1000 * 60 * 60), 2)
    return 0

def get_top_artist_song(access_token, top_artist):
    if not top_artist or 'id' not in top_artist:
        return None
    artist_id = top_artist['id']
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['tracks']:
            top_track = data['tracks'][0]
            return {
                'title': top_track['name'],
                'album': top_track['album']['name'],
                'preview_url': top_track['preview_url'],
                'image_url': top_track['album']['images'][0]['url'] if top_track['album']['images'] else None
            }
    return None

def get_recommendations_from_gemini(top_song, top_artists):
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    input_text = (
        f"My favorite song is '{top_song['title']}' by {top_song['artist']} from the album '{top_song['album']}'. "
        f"My top artists are {[artist['name'] for artist in top_artists]}. "
        "In four sentences, please suggest what I would enjoy listening to next and might wear based on these interests. "
        "What are some new artists I may enjoy?"
    )

    try:
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        print(f"Error querying Gemini API: {e}")
        return "There was an issue getting recommendations."

def get_top_tracks_for_artist(access_token, artist_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                'title': track['name'],
                'album': track['album']['name'],
                'preview_url': track.get('preview_url'),
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            for track in data['tracks'][:5]
        ]
    return None

def get_most_listened_artist(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/top/artists?limit=1'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            top_artist = data['items'][0]
            return {
                'id': top_artist['id'],
                'name': top_artist['name']
            }
    return None

def view_wrap(request, pk):
    # Retrieve the specific wrap object by its primary key (pk)
    wrap = get_object_or_404(Wrap, pk=pk)
    # Render the template and pass the wrap object as context
    return render(request, 'wrap_app/view_wrap.html', {'wrap': wrap})

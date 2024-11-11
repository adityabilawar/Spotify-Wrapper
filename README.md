# Spotify Wrapper

A web application that provides an enhanced Spotify profile experience with personalized music insights and social features.

## Features

- **Spotify Authentication**: Secure login with Spotify credentials
- **Profile Dashboard**: View your Spotify profile information
- **Music Insights**: 
  - View your most listened-to song
  - See your top 3 artists with genres
  - Preview song samples when available
- **Social Features**:
  - Invite friends to compare music tastes
  - Share your music profile
- **Customization**:
  - Dark/Light mode toggle
  - Multi-language support (English, Spanish, French)
- **Mobile Responsive**: Optimized for all device sizes

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
```
4. Run migrations:
```bash
python manage.py migrate
```
5. Start the development server:
```bash
python manage.py runserver
```

## Technologies Used

- Django
- Spotify Web API
- HTML/CSS
- JavaScript

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

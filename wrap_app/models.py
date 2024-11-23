from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField  # Useful for storing lists like top artists or tracks
from django.utils.timezone import now


class Wrap(models.Model):
    spotify_username = models.CharField(max_length=255)
    product = models.CharField(max_length=50, default="Unknown")
    top_song = models.CharField(max_length=255, blank=True, null=True)
    top_artists = models.JSONField(blank=True, null=True)  # Store list of top artists as JSON
    listened_genre = models.CharField(max_length=255, blank=True, null=True)
    top_album = models.CharField(max_length=255, blank=True, null=True)
    listened_hours = models.FloatField(blank=True, null=True)
    most_listened_artist = models.JSONField(blank=True, null=True)  # Store most listened artist data
    top_artist_tracks = models.JSONField(blank=True, null=True)  # Store list of tracks for most listened artist
    top_artist_song = models.CharField(max_length=255, blank=True, null=True)
    special_message = models.TextField(blank=True, null=True)
    gemini_recommendations = models.JSONField(blank=True, null=True)  # Store recommendations as JSON
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Wrap for {self.spotify_username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    def date_display(self):
        """Returns a readable date display for use in templates."""
        return self.created_at.strftime('%B %d, %Y')

class DuoMessage(models.Model):
    sender_username = models.CharField(max_length=255, help_text="The Spotify username of the sender.")
    receiver_username = models.CharField(max_length=255, help_text="The Spotify username of the receiver.")
    wrap_data = models.JSONField(help_text="The combined wrap data for the duo wrap.")
    created_at = models.DateTimeField(default=now, help_text="Timestamp when the duo message was created.")

    def __str__(self):
        return f"Duo Wrap from {self.sender_username} to {self.receiver_username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

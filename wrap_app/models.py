from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Wrap(models.Model):
    # Foreign key to associate the wrap with a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wraps")

    # Date of creation for this wrap
    created_at = models.DateTimeField(default=timezone.now)

    # Time range of the wrap (short_term, medium_term, long_term)
    TIME_RANGE_CHOICES = [
        ('short_term', 'Last 4 Weeks'),
        ('medium_term', 'Last 6 Months'),
        ('long_term', 'All Time'),
    ]
    time_range = models.CharField(max_length=20, choices=TIME_RANGE_CHOICES, default='medium_term')

    # Top songs, artists, and genres stored as JSON data
    top_tracks = models.JSONField(blank=True, null=True)
    top_artists = models.JSONField(blank=True, null=True)
    top_genres = models.JSONField(blank=True, null=True)

    # Additional fields for other Spotify statistics
    listened_hours = models.FloatField(default=0.0)
    first_song = models.JSONField(blank=True, null=True)  # Store first song of the year data as JSON
    most_listened_artist = models.JSONField(blank=True, null=True)  # Most listened artist and relevant data

    # Any special message generated for the wrap
    special_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_time_range_display()} Wrap on {self.created_at.strftime('%Y-%m-%d')}"

    def date_display(self):
        """Returns a readable date display for use in templates."""
        return self.created_at.strftime('%B %d, %Y')

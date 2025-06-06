# accounts/models.py
from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    # Link to Django’s built-in User (or to a custom USER_MODEL if you change that later)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    # Extra fields from your ERD:
    is_host = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    accessibility_needs = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}’s profile"

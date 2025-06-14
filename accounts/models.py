from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    is_host = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to="profiles/", blank=True, null=True
    )
    accessibility_needs = models.TextField(blank=True)

    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} Profile"

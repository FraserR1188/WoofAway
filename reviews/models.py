from django.db import models
from django.conf import settings
from listings.models import Listing
from storages.backends.s3boto3 import S3Boto3Storage

s3 = S3Boto3Storage()


class Review(models.Model):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i>1 else ''}") for i in range(1, 6)]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "guest")  
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review #{self.pk} ({self.rating} ⭐) by {self.guest.username}"

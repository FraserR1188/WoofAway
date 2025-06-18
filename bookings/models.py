# bookings/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from listings.models import Listing
from accounts.models import UserProfile  # if you need host info from profile


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    total_price = models.PositiveIntegerField(blank=True, null=True)
    num_dogs = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.pk} by {self.guest.username} for {self.listing.title}"

    def get_absolute_url(self):
        return reverse("bookings:booking_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        # Auto-calc total_price = nights * listing.price_per_night
        if self.check_in and self.check_out and self.listing:
            nights = (self.check_out - self.check_in).days
            if nights > 0:
                self.total_price = nights * self.listing.price_per_night
            else:
                self.total_price = 0
        super().save(*args, **kwargs)

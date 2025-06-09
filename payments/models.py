# payments/models.py
from django.db import models
from bookings.models import Booking

class Payment(models.Model):
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="payment"
    )
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    # billing address
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
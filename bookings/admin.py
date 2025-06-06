# bookings/admin.py
from django.contrib import admin
from .models import Booking, Payment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "guest",
        "listing",
        "check_in",
        "check_out",
        "status",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("guest__username", "listing__title")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "status", "stripe_payment_intent", "timestamp")
    list_filter = ("status", "timestamp")
    search_fields = ("stripe_payment_intent",)

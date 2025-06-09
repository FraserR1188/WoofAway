# bookings/admin.py
from django.contrib import admin
from .models import Booking

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

# payments/admin.py

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("pk", "booking", "status", "timestamp")
    list_filter = ("status",)
    search_fields = ("booking__pk",)

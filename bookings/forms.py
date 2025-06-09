# bookings/forms.py

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from .models import Booking, Payment


class BookingForm(forms.ModelForm):
    # Visible date‐range picker
    date_range = forms.CharField(
        label="Select Dates",
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "DD-MM-YYYY to DD-MM-YYYY"
        }),
        help_text="Click to choose check-in and check-out dates"
    )

    class Meta:
        model = Booking
        fields = ["date_range", "check_in", "check_out"]
        widgets = {
            "check_in": forms.HiddenInput(),
            "check_out": forms.HiddenInput(),
        }

    def clean(self):
        """
        Validate the date_range format and split into check_in/check_out.
        """
        cleaned = super().clean()
        dr = cleaned.get("date_range")
        if not dr:
            raise ValidationError("Please select a date range.")
        parts = dr.split(" to ")
        if len(parts) != 2:
            raise ValidationError(
                "Date range must be in format 'YYYY-MM-DD to YYYY-MM-DD'."
            )
        start, end = parts
        try:
            d1 = datetime.strptime(start, "%Y-%m-%d").date()
            d2 = datetime.strptime(end,   "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Dates must be in YYYY-MM-DD format.")
        if d2 <= d1:
            raise ValidationError("Check-out must be after check-in.")
        cleaned["check_in"]  = d1
        cleaned["check_out"] = d2
        return cleaned

    def save(self, user, listing, commit=True):
        """
        Assign guest & listing, then save the Booking.
        """
        booking = super().save(commit=False)
        booking.guest   = user
        booking.listing = listing
        if commit:
            booking.save()
        return booking


class PaymentDetailForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["street_address", "city", "postcode", "country"]
        widgets = {
            "street_address": forms.TextInput(attrs={"class": "form-control"}),
            "city":           forms.TextInput(attrs={"class": "form-control"}),
            "postcode":       forms.TextInput(attrs={"class": "form-control"}),
            "country":        forms.TextInput(attrs={"class": "form-control"}),
        }

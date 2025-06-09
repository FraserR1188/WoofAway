# bookings/forms.py

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from .models import Booking

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

    # Address fields
    street_address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    postcode = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # IMPORTANT: The "Save to profile" checkbox
    save_address = forms.BooleanField(
        label="Save this address to my profile",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Booking
        fields = [
            "date_range", "check_in", "check_out",
            "street_address", "city", "postcode", "country",
            "save_address",
        ]
        widgets = {
            "check_in": forms.HiddenInput(),
            "check_out": forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Pop `user` out of kwargs so we can prefill the address
        from the user's profile if it exists.
        """
        super().__init__(*args, **kwargs)

        if user and hasattr(user, "profile"):
            profile = user.profile
            self.fields["street_address"].initial = profile.street_address
            self.fields["city"].initial           = profile.city
            self.fields["postcode"].initial       = profile.postcode
            self.fields["country"].initial        = profile.country

    def clean(self):
        """
        Validate the date_range format and split it into check_in/check_out.
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
            d2 = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Dates must be in YYYY-MM-DD format.")
        if d2 <= d1:
            raise ValidationError("Check-out must be after check-in.")
        cleaned["check_in"] = d1
        cleaned["check_out"] = d2
        return cleaned

    def save(self, user, listing, commit=True):
        """
        Override save to:
         1) Optionally persist the address back to the user's profile.
         2) Create the Booking instance.
        """
        # 1. Save address to profile if requested
        if self.cleaned_data.get("save_address"):
            profile = user.profile
            profile.street_address = self.cleaned_data["street_address"]
            profile.city           = self.cleaned_data["city"]
            profile.postcode       = self.cleaned_data["postcode"]
            profile.country        = self.cleaned_data["country"]
            profile.save()

        # 2. Save the booking
        booking = super().save(commit=False)
        booking.guest   = user
        booking.listing = listing
        if commit:
            booking.save()
        return booking

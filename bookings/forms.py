# bookings/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Booking
from datetime import datetime

class BookingForm(forms.ModelForm):
    date_range = forms.CharField(
        label="Select Dates",
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "DD-MM-YYYY to DD-MM-YYYY"
        }),
        help_text="Click to choose check-in and check-out dates"
    )

    street_address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    postcode = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Booking
        fields = ["date_range", "check_in", "check_out",
                  "street_address", "city", "postcode", "country"]
        widgets = {
            "check_in": forms.HiddenInput(),
            "check_out": forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        # Expect `user` in kwargs so we can prefill address
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, "profile"):
            profile = user.profile
            # Pre-populate address fields from profile
            self.fields["street_address"].initial = profile.street_address
            self.fields["city"].initial = profile.city
            self.fields["postcode"].initial = profile.postcode
            self.fields["country"].initial = profile.country

    def clean(self):
        cleaned_data = super().clean()
        date_range_str = cleaned_data.get("date_range")
        if not date_range_str:
            raise ValidationError("Please select a date range.")
        parts = date_range_str.split(" to ")
        if len(parts) != 2:
            raise ValidationError("Date range must be in format 'YYYY-MM-DD to YYYY-MM-DD'.")
        start_str, end_str = parts
        try:
            check_in_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        if check_out_date <= check_in_date:
            raise ValidationError("Check-out date must be after check-in date.")
        cleaned_data["check_in"] = check_in_date
        cleaned_data["check_out"] = check_out_date
        return cleaned_data
    
    def form_valid(self, user, listing):
        """
        Called from the view instead of CreateView.form_valid.
        Saves booking + updates user profile.
        """
        # 1. Update the user’s profile
        profile = user.profile
        profile.street_address = self.cleaned_data["street_address"]
        profile.city = self.cleaned_data["city"]
        profile.postcode = self.cleaned_data["postcode"]
        profile.country = self.cleaned_data["country"]
        profile.save()

        # 2. Create the booking
        booking = super().save(commit=False)
        booking.guest   = user
        booking.listing = listing
        booking.save()
        return booking
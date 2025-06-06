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

    class Meta:
        model = Booking
        fields = ["date_range", "check_in", "check_out"]
        widgets = {
            "check_in": forms.HiddenInput(),
            "check_out": forms.HiddenInput(),
        }

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

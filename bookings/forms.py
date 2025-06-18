from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Booking


class BookingForm(forms.ModelForm):
    date_range = forms.CharField(
        label="Select Dates",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "YYYY-MM-DD to YYYY-MM-DD"
        })
    )
    num_dogs = forms.TypedChoiceField(
        coerce=int,
        label="Number of Dogs"
    )

    class Meta:
        model = Booking
        fields = ["date_range", "check_in", "check_out", "num_dogs"]
        widgets = {
            "check_in": forms.HiddenInput(),
            "check_out": forms.HiddenInput(),
        }

    def __init__(self, *args, listing=None, **kwargs):
        super().__init__(*args, **kwargs)
        # build the dropdown based on listing.max_dogs
        if listing:
            max_dogs = listing.max_dogs
        else:
            max_dogs = 1
        self.fields['num_dogs'].choices = [(i, i) for i in range(1, max_dogs + 1)]

    def clean(self):
        cleaned = super().clean()
        dr = cleaned.get("date_range")
        if not dr:
            raise ValidationError("Please select a date range.")
        parts = dr.split(" to ")
        if len(parts) != 2:
            raise ValidationError("Date range must be in format 'YYYY-MM-DD to YYYY-MM-DD'.")
        start, end = parts
        try:
            d1 = datetime.strptime(start, "%Y-%m-%d").date()
            d2 = datetime.strptime(end,   "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Dates must be in YYYY-MM-DD format.")
        if d2 <= d1:
            raise ValidationError("Check-out must be after check-in.")
        cleaned["check_in"], cleaned["check_out"] = d1, d2
        return cleaned

    def save(self, user, listing, commit=True):
        booking = super().save(commit=False)
        booking.guest = user
        booking.listing = listing
        booking.num_dogs = self.cleaned_data['num_dogs']
        # recalc total_price including num_dogs
        nights = (booking.check_out - booking.check_in).days
        booking.total_price = nights * listing.price_per_night * booking.num_dogs
        if commit:
            booking.save()
        return booking

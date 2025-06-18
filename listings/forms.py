# listings/forms.py
from django import forms
from django.core.validators import MinValueValidator
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "category",
            "title",
            "description",
            "location",
            "price_per_night",
            "is_accessible",
            "dog_policy",
            "image",
            "max_dogs",           # ← add it here
        ]
        widgets = {
            "max_dogs": forms.Select(
                attrs={"class": "form-select"},
                choices=[(i, i) for i in range(1, 21)]
            ),
        }

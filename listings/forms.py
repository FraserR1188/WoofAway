from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'category', 'title', 'description',
            'location', 'price_per_night', 'is_accessible',
            'dog_policy', 'image', 'max_dogs',
        ]
        widgets = {
            'max_dogs': forms.Select(choices=[(i, i) for i in range(1, 21)]),
        }

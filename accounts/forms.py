# accounts/forms.py
from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["is_host", "bio", "profile_image", "accessibility_needs",
                  "street_address", "city", "postcode", "country"]

        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "accessibility_needs": forms.Textarea(attrs={"rows": 2}),
        }

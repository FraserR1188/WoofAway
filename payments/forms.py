# payments/forms.py

from django import forms
from .models import Payment

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

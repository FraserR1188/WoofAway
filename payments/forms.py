# payments/forms.py

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Payment


class PaymentDetailForm(forms.ModelForm):
    country = CountryField(
        blank_label="(Select country)",
        default="GB"
    ).formfield(
        widget=CountrySelectWidget(attrs={"class": "form-select"})
    )

    class Meta:
        model = Payment
        fields = ["street_address", "city", "postcode", "country"]
        widgets = {
            "street_address": forms.TextInput(attrs={"class": "form-control"}),
            "city":           forms.TextInput(attrs={"class": "form-control"}),
            "postcode":       forms.TextInput(attrs={"class": "form-control"}),
            # country is handled above
        }

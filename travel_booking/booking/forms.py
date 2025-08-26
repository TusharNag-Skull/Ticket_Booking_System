from django import forms
from .models import Booking


class SearchForm(forms.Form):
    type = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Any"),
            ("Flight", "Flight"),
            ("Train", "Train"),
            ("Bus", "Bus"),
        ),
    )
    source = forms.CharField(required=False)
    destination = forms.CharField(required=False)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["number_of_seats"]
        widgets = {
            "number_of_seats": forms.NumberInput(attrs={"min": 1}),
        }



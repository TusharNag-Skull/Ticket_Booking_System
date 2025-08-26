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
        widget=forms.Select(attrs={
            "class": "form-select",
            "aria-label": "Travel type",
        }),
        label="Type",
    )
    source = forms.CharField(
        required=False,
        label="From",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Departure city/airport/station",
                "aria-label": "From",
                "autocomplete": "off",
            }
        ),
    )
    destination = forms.CharField(
        required=False,
        label="To",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Destination city/airport/station",
                "aria-label": "To",
                "autocomplete": "off",
            }
        ),
    )
    date = forms.DateField(
        required=False,
        label="Date",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "aria-label": "Date",
            }
        ),
    )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["number_of_seats"]
        widgets = {
            "number_of_seats": forms.NumberInput(attrs={"min": 1}),
        }



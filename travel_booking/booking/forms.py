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
    # dynamic passenger fields handled on client; we accept JSON in hidden field
    passenger_payload = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Booking
        fields = ["number_of_seats"]
        widgets = {
            "number_of_seats": forms.NumberInput(attrs={"min": 1}),
        }

    def clean(self):
        cleaned = super().clean()
        seats = cleaned.get("number_of_seats") or 0
        payload = self.cleaned_data.get("passenger_payload", "")
        import json
        try:
            passengers = json.loads(payload) if payload else []
        except Exception:
            passengers = []
        if seats and len(passengers) != seats:
            raise forms.ValidationError("Please provide details for all passengers.")
        # basic validation of each passenger
        for p in passengers:
            name = (p.get("name") or "").strip()
            age = int(p.get("age") or 0)
            if not name or age <= 0:
                raise forms.ValidationError("Passenger name and age are required.")
        cleaned["passenger_details"] = passengers
        if passengers:
            cleaned["primary_passenger_name"] = passengers[0]["name"]
            cleaned["primary_passenger_age"] = int(passengers[0]["age"])
        return cleaned



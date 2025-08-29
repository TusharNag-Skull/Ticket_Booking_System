from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "name@example.com",
        }),
        label="Email",
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Phone number",
            "autocomplete": "tel",
        }),
        label="Phone",
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
                "autocapitalize": "off",
                "autocomplete": "username",
            }),
            "password1": forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "new-password",
            }),
            "password2": forms.PasswordInput(attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            phone = self.cleaned_data.get("phone", "")
            Profile.objects.filter(user=user).update(phone=phone)
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have consistent form-control styling
        self.fields["username"].widget.attrs.setdefault("class", "form-control")
        self.fields["username"].widget.attrs.setdefault("placeholder", "Username")
        self.fields["email"].widget.attrs.setdefault("class", "form-control")
        self.fields["email"].widget.attrs.setdefault("placeholder", "name@example.com")
        # Optional phone is on Profile model; ensure uniform look
        if "phone" in self.fields:
            self.fields["phone"].widget.attrs.setdefault("class", "form-control")
            self.fields["phone"].widget.attrs.setdefault("placeholder", "Phone number")
        # UserCreationForm may ignore Meta widgets depending on version - enforce here
        self.fields["password1"].widget.attrs.setdefault("class", "form-control")
        self.fields["password1"].widget.attrs.setdefault("placeholder", "Password")
        self.fields["password2"].widget.attrs.setdefault("class", "form-control")
        self.fields["password2"].widget.attrs.setdefault("placeholder", "Confirm password")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone",)
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
                "autocomplete": "tel",
            })
        }


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Username",
                "autocapitalize": "off",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )



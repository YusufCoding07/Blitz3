# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Transaction

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class DriverApplicationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['license_file', 'car_model']
        widgets = {
            'license_file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError("Phone number is required for drivers")
        return phone

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']

class RideCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['pickup_location', 'dropoff_location', 'amount']

class RideSearchForm(forms.Form):
    pickup_location = forms.CharField(max_length=200)
    dropoff_location = forms.CharField(max_length=200)
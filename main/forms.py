# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number']

class DriverApplicationForm(forms.ModelForm):
    has_valid_license = forms.BooleanField(
        required=True,
        label='I confirm I have a valid driving license'
    )
    car_model = forms.CharField(
        max_length=100,
        required=True,
        label='Car Model (e.g., Toyota Camry 2020)'
    )

    class Meta:
        model = UserProfile
        fields = ['has_valid_license', 'car_model']
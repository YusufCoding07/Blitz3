# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile  # Add this import

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # ✅ Changed from Profile to UserProfile
        fields = ['profile_picture', 'phone_number']  # Update fields as needed

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
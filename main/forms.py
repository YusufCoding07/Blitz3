# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Ride

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
        fields = ['profile_picture', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class DriverApplicationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'car_model', 'license_file']
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
        fields = ['phone_number', 'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class RideCreateForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'date', 'time', 'price', 'seats_available']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup location'
            }),
            'dropoff_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price'
            }),
            'seats_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '8'
            })
        }

class RideSearchForm(forms.Form):
    pickup = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter pickup location'
    }))
    destination = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter destination'
    }))
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
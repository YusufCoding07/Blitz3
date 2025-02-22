# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, Ride, Transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city (e.g., London)',
                'required': 'required'
            }
        )
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'location', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                location=self.cleaned_data['location']
            )
        return user

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_driver', 'bio', 'location', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class DriverApplicationForm(forms.ModelForm):
    car_model = forms.CharField(max_length=100)
    car_year = forms.IntegerField()
    license_number = forms.CharField(max_length=50)
    
    class Meta:
        model = UserProfile
        fields = ['is_driver', 'car_model', 'car_year', 'license_number']

class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city (e.g., London)'
        })
    )
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'profile_picture']

class RideCreateForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'date', 'time', 'price', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise ValidationError("Date cannot be in the past")
        return date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if date and time:
            datetime_combined = timezone.make_aware(
                timezone.datetime.combine(date, time)
            )
            if datetime_combined < timezone.now():
                raise ValidationError("Ride time cannot be in the past")
        
        return cleaned_data

class RideSearchForm(forms.Form):
    pickup_location = forms.CharField(max_length=200, required=False)
    dropoff_location = forms.CharField(max_length=200, required=False)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
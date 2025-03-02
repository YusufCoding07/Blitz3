from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User , UserProfile , Ride , Transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Ride  # Import the Ride model if needed


class RideCreateForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'date', 'time', 'price']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
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


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['location', 'is_driver', 'bio', 'profile_picture', 'driver_status', 'car_model', 'car_year', 'license_number']  # Update with your actual fields
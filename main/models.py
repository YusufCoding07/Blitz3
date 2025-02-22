from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from django.conf import settings

class User(AbstractUser):
    @property
    def current_ride(self):
        return Ride.objects.filter(
            Q(driver=self) | Q(passenger=self),
            status='accepted'
        ).first()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_driver = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', default='default.jpg')
    driver_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    car_model = models.CharField(max_length=100, blank=True)
    car_year = models.IntegerField(null=True, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.created_at}"

@receiver(post_save, sender='main.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender='main.User')
def save_user_profile(sender, instance, **kwargs):
    try:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        instance.userprofile.save()
    except Exception as e:
        print(f"Error saving user profile: {e}")

class Ride(models.Model):
    RIDE_STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('available', 'Available'),
    )

    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seats = models.IntegerField()
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_driver', null=True, blank=True)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_passenger', null=True, blank=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location} on {self.date}"
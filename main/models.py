from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils import timezone

class UserProfile(models.Model):
    DRIVER_STATUS_CHOICES = [
        ('not_applied', 'Not Applied'),
        ('pending', 'Application Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    driver_status = models.CharField(
        max_length=20,
        choices=DRIVER_STATUS_CHOICES,
        default='not_applied'
    )
    driver_document = models.FileField(
        upload_to='driver_docs/',
        null=True,
        blank=True,
        verbose_name='Driver Documentation'
    )
    application_date = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True, null=True, help_text="Tell us about yourself (optional, max 250 characters)")

    def is_driver(self):
        return self.driver_status == 'approved'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_driver = models.BooleanField(default=False)
    has_valid_license = models.BooleanField(default=False)
    car_model = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    driver_status = models.CharField(
        max_length=20,
        choices=DRIVER_STATUS_CHOICES,
        default='not_applied'
    )
    license_file = models.FileField(upload_to='licenses/', blank=True, null=True)
    application_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.date}"

    class Meta:
        ordering = ['-date']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Ride(models.Model):
    RIDE_STATUS_CHOICES = [
        ('open', 'Open'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_offered')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seats_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=RIDE_STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location} on {self.date}"
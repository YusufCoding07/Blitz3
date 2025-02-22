from django.contrib import admin
from .models import UserProfile, Transaction, Ride

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_driver', 'driver_status', 'car_model']
    list_filter = ['is_driver', 'driver_status']
    search_fields = ['user__username', 'car_model', 'license_number']
    readonly_fields = ['user']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'timestamp', 'description']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'description']

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ['pickup_location', 'dropoff_location', 'date', 'time', 'price', 'status']
    list_filter = ['status', 'date']
    search_fields = ['pickup_location', 'dropoff_location', 'driver__username', 'passenger__username']

from django.contrib import admin
from .models import UserProfile, Transaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_driver', 'has_valid_license')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('is_driver', 'has_valid_license')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'date')
    search_fields = ('user__username', 'description')
    list_filter = ('date',)

from django.contrib import admin
from .models import UserProfile, Transaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_driver', 'driver_status', 'application_date')
    list_filter = ('is_driver', 'driver_status', 'has_valid_license')
    search_fields = ('user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'profile_picture')
        }),
        ('Driver Status', {
            'fields': ('is_driver', 'driver_status', 'has_valid_license', 'car_model')
        }),
        ('Application Details', {
            'fields': ('license_file', 'application_date', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['approve_driver', 'reject_driver']

    def approve_driver(self, request, queryset):
        queryset.update(
            is_driver=True,
            driver_status='approved',
            has_valid_license=True
        )
    approve_driver.short_description = "Approve selected driver applications"

    def reject_driver(self, request, queryset):
        queryset.update(
            is_driver=False,
            driver_status='rejected',
            has_valid_license=False
        )
    reject_driver.short_description = "Reject selected driver applications"

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'date')
    search_fields = ('user__username', 'description')
    list_filter = ('date',)

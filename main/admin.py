from django.contrib import admin
from .models import UserProfile, Transaction

# Register your models
admin.site.register(UserProfile)
admin.site.register(Transaction)

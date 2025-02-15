import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Profile  # Add this import

class Command(BaseCommand):
    help = 'Creates a superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_username = os.getenv('DEFAULT_ADMIN_USERNAME')
        admin_email = os.getenv('DEFAULT_ADMIN_EMAIL')
        admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD')

        # Check if the user already exists
        user_exists = User.objects.filter(username=admin_username).exists()
        
        if not user_exists:
            # Create the superuser
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS('Superuser created!'))
            
            # Ensure the profile exists
            Profile.objects.get_or_create(user=user)
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_username = os.getenv('DEFAULT_ADMIN_USERNAME')
        admin_email = os.getenv('DEFAULT_ADMIN_EMAIL')
        admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS('Superuser created!'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))
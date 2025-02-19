from django.db import migrations
from django.contrib.auth.models import User
from django.db.models import F

def create_missing_profiles(apps, schema_editor):
    UserProfile = apps.get_model('main', 'UserProfile')
    User = apps.get_model('auth', 'User')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_fix_userprofile_table'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, reverse_code=migrations.RunPython.noop),
    ]
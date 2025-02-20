from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='driver_status',
            field=models.CharField(
                choices=[
                    ('not_applied', 'Not Applied'),
                    ('pending', 'Application Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected')
                ],
                default='not_applied',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='license_file',
            field=models.FileField(blank=True, null=True, upload_to='licenses/'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='application_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='admin_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ] 
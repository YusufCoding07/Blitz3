from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_add_driver_application_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='description',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='date',
        ),
        migrations.AddField(
            model_name='transaction',
            name='pickup_location',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='dropoff_location',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('accepted', 'Accepted'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),
    ] 
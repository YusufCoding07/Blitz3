from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('main', 'XXXX_previous_migration'),  # Replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='driver',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='driven_transactions',
                to='auth.user'
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(
                choices=[('ride', 'Ride Posting'), ('payment', 'Payment'), ('earning', 'Earning')],
                default='ride',
                max_length=20
            ),
        ),
    ] 
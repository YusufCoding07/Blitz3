from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_transaction_options_alter_userprofile_options'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS main_profile CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ] 
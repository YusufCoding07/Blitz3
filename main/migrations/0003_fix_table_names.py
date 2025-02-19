from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS main_profile CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ] 
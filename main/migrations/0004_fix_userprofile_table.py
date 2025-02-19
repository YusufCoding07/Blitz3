from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_fix_table_names'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE IF EXISTS main_profile 
            RENAME TO main_userprofile;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ] 
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_fix_users_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users_user ADD COLUMN IF NOT EXISTS is_staff boolean NOT NULL DEFAULT false;",
            reverse_sql="ALTER TABLE users_user DROP COLUMN IF EXISTS is_staff;",
        ),
    ]
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_add_is_staff'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users_user ALTER COLUMN is_admin SET DEFAULT false;",
            reverse_sql="ALTER TABLE users_user ALTER COLUMN is_admin DROP DEFAULT;",
        ),
    ]
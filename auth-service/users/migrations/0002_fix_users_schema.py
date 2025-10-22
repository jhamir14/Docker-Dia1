from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Agregar columna is_superuser en la tabla existente si no existe
        migrations.RunSQL(
            sql="ALTER TABLE users_user ADD COLUMN IF NOT EXISTS is_superuser boolean NOT NULL DEFAULT false;",
            reverse_sql="ALTER TABLE users_user DROP COLUMN IF EXISTS is_superuser;",
        ),
        # Agregar columna is_staff (si la tabla tiene is_admin, mantenemos ambas por compatibilidad)
        migrations.RunSQL(
            sql="ALTER TABLE users_user ADD COLUMN IF NOT EXISTS is_staff boolean NOT NULL DEFAULT false;",
            reverse_sql="ALTER TABLE users_user DROP COLUMN IF EXISTS is_staff;",
        ),
    ]
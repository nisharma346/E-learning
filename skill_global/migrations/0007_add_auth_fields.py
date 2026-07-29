from django.db import migrations, models


def copy_name_to_fullname(apps, schema_editor):
    CustomUser = apps.get_model('skill_global', 'CustomUser')
    for user in CustomUser.objects.all():
        try:
            name = getattr(user, 'name', None)
            if name and not getattr(user, 'full_name', None):
                user.full_name = name
                user.save()
        except Exception:
            # in migrations we must not fail on individual rows
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0006_profile'),
    ]

    operations = [
        # Add missing columns that AbstractUser expects. SQLite allows ADD COLUMN.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE skill_global_customuser ADD COLUMN username varchar(150);",
                "ALTER TABLE skill_global_customuser ADD COLUMN last_login datetime;",
                "ALTER TABLE skill_global_customuser ADD COLUMN is_superuser integer NOT NULL DEFAULT 0;",
                "ALTER TABLE skill_global_customuser ADD COLUMN first_name varchar(150) NOT NULL DEFAULT '';",
                "ALTER TABLE skill_global_customuser ADD COLUMN last_name varchar(150) NOT NULL DEFAULT '';",
                "ALTER TABLE skill_global_customuser ADD COLUMN is_staff integer NOT NULL DEFAULT 0;",
                "ALTER TABLE skill_global_customuser ADD COLUMN is_active integer NOT NULL DEFAULT 1;",
                "ALTER TABLE skill_global_customuser ADD COLUMN date_joined datetime;",
                "ALTER TABLE skill_global_customuser ADD COLUMN full_name varchar(255);",
                "ALTER TABLE skill_global_customuser ADD COLUMN bio text;",
                "ALTER TABLE skill_global_customuser ADD COLUMN profile_image varchar(100);",
            ],
            reverse_sql=[
                # SQLite can't drop columns; provide noop reverse (manual rollback required)
            ],
        ),
        migrations.RunPython(copy_name_to_fullname, reverse_code=migrations.RunPython.noop),
    ]

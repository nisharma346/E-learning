from django.conf import settings
from django.db import migrations


def rebuild_profile_table(apps, schema_editor):
    connection = schema_editor.connection
    quoted = connection.ops.quote_name

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            CREATE TABLE {quoted('skill_global_profile_new')} (
                {quoted('id')} integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                {quoted('phone')} varchar(20) NOT NULL,
                {quoted('bio')} text NOT NULL,
                {quoted('image')} varchar(100) NULL,
                {quoted('created_at')} datetime NOT NULL,
                {quoted('updated_at')} datetime NOT NULL,
                {quoted('user_id')} integer NOT NULL UNIQUE
                    REFERENCES {quoted('skill_global_customuser')} ({quoted('id')})
                    DEFERRABLE INITIALLY DEFERRED
            )
            """
        )
        cursor.execute(
            f"""
            INSERT INTO {quoted('skill_global_profile_new')}
                ({quoted('id')}, {quoted('phone')}, {quoted('bio')},
                 {quoted('image')}, {quoted('created_at')}, {quoted('updated_at')},
                 {quoted('user_id')})
            SELECT profile.{quoted('id')}, profile.{quoted('phone')}, profile.{quoted('bio')},
                   profile.{quoted('image')}, profile.{quoted('created_at')},
                   profile.{quoted('updated_at')}, profile.{quoted('user_id')}
            FROM {quoted('skill_global_profile')} AS profile
            INNER JOIN {quoted('skill_global_customuser')} AS user
                ON user.{quoted('id')} = profile.{quoted('user_id')}
            """
        )
        cursor.execute(
            f"DROP TABLE {quoted('skill_global_profile')}"
        )
        cursor.execute(
            f"ALTER TABLE {quoted('skill_global_profile_new')} RENAME TO {quoted('skill_global_profile')}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0015_coupon_courseenrollment_discount_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(rebuild_profile_table, migrations.RunPython.noop),
    ]
# Generated by Django 4.2.18 on 2025-03-08 03:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_user_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_picture',
        ),
    ]

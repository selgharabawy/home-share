# Generated by Django 4.2.9 on 2024-01-09 19:16

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_gender_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=user.models.user_image_file_path),
        ),
    ]
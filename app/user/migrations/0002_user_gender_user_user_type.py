# Generated by Django 4.2.8 on 2024-01-03 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1),
        ),
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('home_seeker', 'Home Seeker'), ('property_owner', 'Property Owner'), ('admin', 'Administrator')], default='admin', max_length=14),
        ),
    ]
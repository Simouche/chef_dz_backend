# Generated by Django 3.0.5 on 2020-07-09 17:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0018_auto_20200708_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator('^\\+?[0-9]{,12}$', "The phone number you entered is not valid it must be of the international format.example '+213799136332'", 'Invalid PhoneNumber')]),
        ),
    ]

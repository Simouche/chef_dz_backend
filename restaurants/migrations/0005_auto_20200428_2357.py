# Generated by Django 3.0.5 on 2020-04-28 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0004_appversion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsverification',
            name='otp_code',
            field=models.CharField(max_length=5),
        ),
    ]

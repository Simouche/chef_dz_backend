# Generated by Django 3.0.5 on 2020-07-08 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0016_auto_20200629_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

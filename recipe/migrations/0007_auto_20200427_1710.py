# Generated by Django 3.0.5 on 2020-04-27 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0001_initial'),
        ('recipe', '0006_auto_20200425_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='profile', to='restaurants.Client', unique=True),
        ),
    ]

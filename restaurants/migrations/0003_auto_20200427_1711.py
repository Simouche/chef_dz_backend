# Generated by Django 3.0.5 on 2020-04-27 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0008_auto_20200427_1711'),
        ('restaurants', '0002_auto_20200427_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='participant',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='participant', to='recipe.Participant'),
        ),
    ]

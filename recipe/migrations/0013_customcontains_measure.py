# Generated by Django 3.0.5 on 2020-05-07 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0012_auto_20200502_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='customcontains',
            name='measure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='recipe.QuantityMeasure'),
        ),
    ]

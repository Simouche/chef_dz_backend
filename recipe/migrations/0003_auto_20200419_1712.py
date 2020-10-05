# Generated by Django 3.0.5 on 2020-04-19 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0001_initial'),
        ('recipe', '0002_auto_20200418_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cuisine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipe_cuisine', to='restaurants.Cuisine'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipe_type', to='restaurants.MealType'),
        ),
    ]

# Generated by Django 3.0.5 on 2020-04-25 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20200425_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='comments', to='recipe.Recipe'),
        ),
        migrations.AlterField(
            model_name='like',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='likes', to='recipe.Recipe'),
        ),
        migrations.AlterField(
            model_name='starsrate',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stars', to='recipe.Recipe'),
        ),
        migrations.AlterUniqueTogether(
            name='recipe',
            unique_together={('published_by', 'food_name')},
        ),
    ]

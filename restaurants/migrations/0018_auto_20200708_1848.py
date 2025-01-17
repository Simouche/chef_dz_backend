# Generated by Django 3.0.5 on 2020-07-08 17:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0017_auto_20200708_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='default',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^\\+?[0-9]{,12}$', "The phone number you entered is not valid it must be of the international format.example '+213799136332'", 'Invalid PhoneNumber')])),
                ('default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='phones', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

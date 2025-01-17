# Generated by Django 3.0.5 on 2020-04-18 12:25

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('notification_token', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('phone', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^\\+?[0-9]{,12}$', "The phone number you entered is not valid it must be of the international format.example '+213799136332'", 'Invalid PhoneNumber')], verbose_name='Phone Number')),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('photo', models.ImageField(blank=True, help_text="the user's profile picture.", null=True, upload_to='profile/', verbose_name='Profile Picture')),
                ('address', models.CharField(max_length=255, verbose_name='Address')),
                ('user_type', models.CharField(choices=[('C', 'Client'), ('S', 'Restaurant Staff'), ('O', 'Restaurant Owner'), ('A', 'Admin'), ('D', 'Delivery Guy')], help_text="The user's type can be one of the available choices, refer to the Model class for the detailed list.", max_length=3, verbose_name='Type')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Birth Date')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('code_postal', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_participant', models.BooleanField(default=False)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='client', to=settings.AUTH_USER_MODEL)),
                ('participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='participant', to='recipe.Participant')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MealType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number', models.IntegerField()),
                ('name', models.CharField(max_length=150, unique=True)),
                ('description', models.TextField()),
                ('price', models.FloatField()),
                ('image', models.ImageField(upload_to='menu/')),
                ('discount', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OfferType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('number', models.IntegerField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('token', models.CharField(editable=False, max_length=255)),
                ('used', models.BooleanField(default=False)),
                ('email', models.EmailField(blank=True, editable=False, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, editable=False, max_length=20, null=True)),
                ('otp_code', models.CharField(blank=True, editable=False, max_length=5, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=150)),
                ('registre_commerce', models.CharField(max_length=150, unique=True)),
                ('id_fiscale', models.CharField(max_length=150, unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('address', models.CharField(max_length=150)),
                ('images', models.CharField(blank=True, max_length=255, unique=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.City')),
                ('main_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RestaurantType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SmsVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('otp_code', models.CharField(editable=False, max_length=5)),
                ('number', models.CharField(editable=False, max_length=255, validators=[django.core.validators.RegexValidator('^\\+?[0-9]{,12}$', "The phone number you entered is not valid it must be of the international format.example '+213799136332'", 'Invalid PhoneNumber')])),
                ('confirmed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Wilaya',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('matricule', models.IntegerField()),
                ('code_postal', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('total', models.FloatField(default=0.0)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Menu')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='menu',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.OfferType'),
        ),
        migrations.AddField(
            model_name='menu',
            name='offered_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Restaurant'),
        ),
        migrations.AddField(
            model_name='menu',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.MealType'),
        ),
        migrations.AddField(
            model_name='city',
            name='wilaya',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Wilaya'),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('address', models.CharField(max_length=150)),
                ('belongs_to', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='addresses', to='restaurants.Client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='lives_in',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.City'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='WorksAt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Restaurant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'restaurant', 'visible')},
            },
        ),
        migrations.CreateModel(
            name='RestaurantTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Restaurant')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.RestaurantType')),
            ],
            options={
                'unique_together': {('type', 'restaurant')},
            },
        ),
        migrations.CreateModel(
            name='RestaurantMealTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Restaurant')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.MealType')),
            ],
            options={
                'unique_together': {('type', 'restaurant')},
            },
        ),
        migrations.CreateModel(
            name='RestaurantCuisines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cuisine', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Cuisine')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='restaurants.Restaurant')),
            ],
            options={
                'unique_together': {('cuisine', 'restaurant')},
            },
        ),
    ]

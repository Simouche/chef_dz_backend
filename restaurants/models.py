import os
from datetime import date
from functools import reduce

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Count, Avg
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base_backend.messaging import notify_user
from base_backend.models import BaseModel, do_nothing, DeletableModel, Round, cascade
from base_backend.tracking_funcs import measure
from base_backend.validators import phone_validator
from restaurant.settings import MEDIA_ROOT, RESTAURANT_IMAGES_URL
from restaurants.managers import CustomMenusManager


class User(AbstractUser):
    USER_TYPES = (('C', _('Client')), ('S', _('Restaurant Staff')), ('O', _('Restaurant Owner')), ('A', _('Admin'))
                  , ('D', _('Delivery Guy')))
    GENDERS = (('M', 'Male'), ('F', 'Female'))

    notification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    phone = models.CharField(
        _("Phone Number"),
        max_length=50,
        validators=[phone_validator],
        unique=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    photo = models.ImageField(
        _('Profile Picture'),
        upload_to='profile/',
        help_text=_(
            "the user's profile picture."
        ),
        blank=True,
        null=True
    )
    address = models.CharField(_("Address"), max_length=255)
    lives_in = models.ForeignKey('City', on_delete=do_nothing, null=True, blank=True)
    user_type = models.CharField(
        _("Type"),
        max_length=3,
        choices=USER_TYPES,
        help_text=_("The user's type can be one of the available choices, "
                    "refer to the Model class for the detailed list."),
    )
    birth_date = models.DateField(_('Birth Date'), blank=True, null=True)
    gender = models.CharField(choices=GENDERS, max_length=1, default='M')

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", 'user_type', 'phone', 'email']

    @property
    def full_name(self):
        return "{} {}".format(self.last_name, self.first_name)

    @property
    def get_age(self) -> int:
        today = date.today()
        dob = self.birth_date
        before_dob = (today.month, today.day) < (dob.month, dob.day)
        return today.year - self.birth_date.year - before_dob

    @property
    def confirmed_phone(self) -> bool:
        return False

    @property
    def confirmed_email(self) -> bool:
        return False

    @property
    def scores(self):
        scores = None
        if self.client and self.client.is_participant and self.client.participant:
            from recipe.models import Participant
            scores = Participant.objects.filter(pk=self.client.participant.pk) \
                .annotate(likes_=Count("recipes__likes")).annotate(avg=Round(Avg('recipes__stars__stars'), 1))[0]
        return scores

    @property
    def get_photo(self):
        try:
            return self.photo.url
        except ValueError:
            return ""

    def __str__(self):
        return self.full_name


class Client(BaseModel):
    owner = models.OneToOneField('User', on_delete=models.DO_NOTHING, related_name='client')
    is_participant = models.BooleanField(default=False)
    participant = models.OneToOneField('recipe.Participant', on_delete=do_nothing, null=True, blank=True,
                                       related_name='participant', unique=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.owner.__str__()


class Restaurant(DeletableModel):
    name = models.CharField(max_length=150)
    registre_commerce = models.CharField(max_length=150, unique=True)
    id_fiscale = models.CharField(max_length=150, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    main_user = models.ForeignKey('User', on_delete=do_nothing)
    address = models.CharField(max_length=150)
    city = models.ForeignKey('City', on_delete=do_nothing)
    logo = models.ImageField(upload_to="logo/", null=True)
    images = models.CharField(max_length=255, unique=True, blank=True, null=True)
    phone = models.CharField(unique=True, null=True, blank=True, validators=[phone_validator], max_length=30)
    email = models.EmailField(unique=True, null=True, blank=True, )
    description = models.TextField(null=True)
    open_at = models.TimeField(null=True)
    close_at = models.TimeField(null=True)

    on_special_day = models.BooleanField(default=False)
    global_discount = models.FloatField(default=0)

    cuisines = models.ManyToManyField('Cuisine', through='RestaurantCuisines')
    types = models.ManyToManyField('RestaurantType', through='RestaurantTypes')
    meal_types = models.ManyToManyField('MealType', through='RestaurantMealTypes')

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        super(Restaurant, self).save(**kwargs)
        if not self.images:
            self.images = os.path.join(MEDIA_ROOT, 'restaurants', str(self.pk))
            os.makedirs(self.images, exist_ok=True)
            super(Restaurant, self).save(**kwargs)

    @property
    def images_urls(self):
        images_urls = []
        if self.images:
            images_names = os.listdir(self.images)
            for name in images_names:
                images_urls.append(RESTAURANT_IMAGES_URL + str(self.pk) + "/" + name)
        return images_urls


class RestaurantType(BaseModel):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type


class Cuisine(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class MealType(BaseModel):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type


class OfferType(BaseModel):
    type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type


class RestaurantCuisines(BaseModel):
    cuisine = models.ForeignKey('Cuisine', on_delete=do_nothing)
    restaurant = models.ForeignKey('Restaurant', on_delete=do_nothing)

    class Meta:
        unique_together = (('cuisine', 'restaurant'),)

    def __str__(self):
        return "Restaurant: {} Has the cuisine: {}".format(self.restaurant, self.cuisine)


class RestaurantTypes(BaseModel):
    restaurant = models.ForeignKey('Restaurant', on_delete=do_nothing)
    type = models.ForeignKey('RestaurantType', on_delete=do_nothing)

    class Meta:
        unique_together = (('type', 'restaurant'),)

    def __str__(self):
        return "Restaurant: {}  type is : {}".format(self.restaurant, self.type)


class RestaurantMealTypes(BaseModel):
    restaurant = models.ForeignKey('Restaurant', on_delete=do_nothing)
    type = models.ForeignKey('MealType', on_delete=do_nothing)

    class Meta:
        unique_together = (('type', 'restaurant'),)

    def __str__(self):
        return "Restaurant: {} Has meal type: {}".format(self.restaurant, self.type)


class Menu(BaseModel):
    number = models.IntegerField()
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='menu/')
    offered_by = models.ForeignKey('Restaurant', on_delete=do_nothing, related_name='menus')
    type = models.ForeignKey('MealType', on_delete=do_nothing, related_name='menus')
    offer = models.ForeignKey('OfferType', on_delete=do_nothing, related_name='menus')
    cuisine = models.ForeignKey('Cuisine', on_delete=do_nothing, related_name='menus', null=True)
    discount = models.IntegerField(null=True, blank=True, default=0)

    objects = CustomMenusManager()

    @property
    def get_current_price(self) -> float:
        return self.price - self.discount_amount

    @property
    def discount_amount(self) -> float:
        return (self.price * (float(self.discount))) / 100.0

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'offered_by'),)


class OrderLine(BaseModel):
    number = models.IntegerField()
    menu = models.ForeignKey('Menu', on_delete=do_nothing)
    quantity = models.IntegerField()
    total = models.FloatField(default=0.0)
    comment = models.CharField(max_length=255, null=True)
    order = models.ForeignKey('Order', on_delete=cascade, related_name='lines')

    def save(self, *args, **kwargs):
        self.total = float(self.quantity) * self.menu.get_current_price
        super(OrderLine, self).save(*args, **kwargs)

    @property
    def discount_amount(self) -> float:
        return float(self.quantity) * self.menu.discount_amount

    def __str__(self):
        return "Line {} of the Order {}".format(self.number, self.order)


class Order(DeletableModel):
    previous_status = None
    STATUS = (('P', _('Pending')), ('A', _('Accepted')), ('R', _('Ready')), ('Pi', _('Picked')), ('D', _('Delivered')))

    status = models.CharField(max_length=2, default='P', choices=STATUS)
    number = models.IntegerField()
    client = models.ForeignKey('Client', on_delete=do_nothing)
    restaurant = models.ForeignKey('Restaurant', on_delete=do_nothing, related_name='orders', null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator], blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    building = models.IntegerField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)

    @property
    def total(self):
        return self.sub_total - self.discount_total + self.delivery_fees

    @property
    def sub_total(self) -> float:
        total = self.lines.all().aggregate(Sum("total")).get("total__sum")
        return total

    @property
    def restaurant_discount(self):
        return (self.sub_total * (float(self.restaurant.global_discount))) / 100.0

    @property
    def menus_discount(self):
        return sum([x.discount_amount for x in self.lines.all()])

    @property
    def discount_total(self) -> float:
        return self.menus_discount + self.restaurant_discount

    @property
    def delivery_fees(self):
        if not self.latitude or not self.longitude:
            return 0
        return measure(self.latitude, self.longitude, self.restaurant.latitude, self.restaurant.longitude) * 20.0

    def __str__(self):
        return "{0} {1}".format(self.number, self.client.__str__())

    @staticmethod
    def generate_number():
        from random import randint
        return randint(11111, 99999)


class WorksAt(DeletableModel):
    user = models.ForeignKey('User', on_delete=do_nothing)
    restaurant = models.ForeignKey('Restaurant', on_delete=do_nothing)

    class Meta:
        unique_together = (('user', 'restaurant', 'visible'),)

    def __str__(self):
        return "User {} works at {}".format(self.user, self.restaurant)


class Wilaya(BaseModel):
    name = models.CharField(max_length=255)
    matricule = models.IntegerField()
    code_postal = models.IntegerField()

    def __str__(self):
        return "{0} {1}".format(self.matricule, self.name)


class City(BaseModel):
    name = models.CharField(max_length=255)
    code_postal = models.IntegerField()
    wilaya = models.ForeignKey('Wilaya', on_delete=models.DO_NOTHING, related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class Address(DeletableModel):
    address = models.CharField(max_length=150)
    belongs_to = models.ForeignKey('Client', on_delete=do_nothing, related_name='addresses')
    default = models.BooleanField(default=False)

    def __str__(self):
        return "Another Address of the User {}".format(self.belongs_to)


class Phone(DeletableModel):
    phone = models.CharField(validators=[phone_validator], max_length=20)
    user = models.ForeignKey('User', on_delete=do_nothing, related_name='phones')
    default = models.BooleanField(default=False)

    def __str__(self):
        return "Another Address of the User {}".format(self.user)


class SmsVerification(BaseModel):
    otp_code = models.CharField(max_length=5)
    number = models.CharField(validators=[phone_validator], max_length=255, editable=False)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return "{} is {}".format(self.number, 'Confirmed' if self.confirmed else 'Not Confirmed')


class PasswordReset(BaseModel):
    token = models.CharField(editable=False, max_length=255, null=False)
    used = models.BooleanField(default=False)
    email = models.EmailField(editable=False, null=True, blank=True)
    phone = models.CharField(max_length=20, editable=False, null=True, blank=True)
    otp_code = models.CharField(max_length=5, editable=False, null=True, blank=True)


class AppVersion(models.Model):
    code = models.IntegerField(default=0)

    def __str__(self):
        return str(self.code)


@receiver(post_save, sender=User)
def send_sms_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        # from base_backend.utils import phone_sms_verification
        # phone_sms_verification(instance.phone)
        # if instance.user_type == 'C':
        #     Address.objects.create(address=instance.address, belongs_to=instance.client)
        instance.is_active = True
        instance.save()


@receiver(post_save, sender=Order)
def order_status_update(sender, instance, **kwargs):
    if kwargs.get('created', False):
        notify_user(instance.restaurant.owner.notification_token,
                    {'title': 'new order', 'message': 'You have a new order'})
    else:
        if instance.previous_status == instance.status:
            return
        elif instance.status == 'A':
            notify_user(instance.client.owner.notification_token,
                        {'title': 'Order accepted', 'message': 'Your order have been accepted'})
        elif instance.status == 'R':
            # TODO: notify the delivery and user
            notify_user(instance.client.owner.notification_token,
                        {'title': 'Order ready', 'message': 'Your order is ready'})
        elif instance.status == 'Pi':
            notify_user(instance.client.owner.notification_token,
                        {'title': 'Order picked', 'message': 'Your order is picked'})
        elif instance.status == 'D':
            notify_user(instance.client.owner.notification_token,
                        {'title': 'Order delivered', 'message': 'Your order has been delivered'})
            notify_user(instance.restaurant.owner.notification_token,
                        {'title': 'Order delivered', 'message': 'Your order has been delivered'})


@receiver(post_init, sender=Order)
def mark_order_previous_status(sender, instance, **kwargs):
    instance.previous_status = instance.previous_status

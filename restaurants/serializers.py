from django.contrib.auth.models import Group
from django.db.models import Sum, Avg
from rest_framework import serializers

from base_backend.utils import activate_user_over_otp, phone_reconfirmation
from delivery.models import DeliveryGuy, VehicleType

from recipe.models import Participant
from restaurants.models import (User, SmsVerification, Client, Restaurant, Menu, OrderLine, Order, Wilaya, City,
                                Address, OfferType,
                                Cuisine, MealType, RestaurantType, Phone)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address', 'belongs_to', 'default']


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['phone', 'user', 'default']
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.ChoiceField(choices=VehicleType.objects.all().values_list('type', flat=True),
                                           required=False)
    client = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    def validate(self, attrs):
        if attrs.get('user_type') == 'D' and not attrs.get('vehicle_type'):
            raise serializers.ValidationError("The delivery guy should have a vehicle")

        return super(UserSerializer, self).validate(attrs)

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        user_type = validated_data.get('user_type')

        if user_type == 'C':
            user.groups.add(Group.objects.get(name='client'))
            user.groups.add(Group.objects.get(name='participant'))
            client = Client.objects.create(owner=user, is_participant=True)
            client.participant = Participant.objects.create(profile=client)
            client.save()
        elif user_type == 'D':
            user.groups.add(Group.objects.get(name='delivery'))
            DeliveryGuy.objects.create(owner=user, vehicle=validated_data.get('vehicle_type'))
        elif user_type == 'A':
            user.groups.add(Group.objects.get(name='admin'))
        elif user_type == 'S':
            user.groups.add(Group.objects.get(name='staff'))
        elif user_type == 'O':
            user.groups.add(Group.objects.get(name='owner'))

        return user

    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name', 'last_name', 'birth_date', 'gender', 'user_type', 'password',
                  'username', 'vehicle_type', 'client', 'participant', 'photo', 'gender', 'full_name', 'address',
                  'stars']
        extra_kwargs = {
            "password": {"write_only": True},
            'client': {'read_only': True},
            'participant': {'read_only': True},
            'photo': {'required': False},
            'gender': {'required': False},
            'address': {'required': False},
        }

    def get_client(self, obj):
        if Group.objects.get(name='client') in obj.groups.all():
            return obj.client.id
        return None

    def get_participant(self, obj):
        if Group.objects.get(name='participant') in obj.groups.all():
            return obj.client.participant.pk
        return None

    def get_stars(self, obj):
        if Group.objects.get(name='participant') in obj.groups.all():
            return obj.client.participant.recipes.aggregate(sum=Sum('stars__stars')).get('sum')
        return None


class ClientSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Client
        fields = ['owner', 'is_participant']


class SmsConfirmationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get('otp_code') and not attrs.get('phone'):
            raise serializers.ValidationError("You should provide either a code or a phone number")

        return super(SmsConfirmationSerializer, self).validate(attrs)

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None

    def activate(self):
        self.is_valid(raise_exception=True)
        return activate_user_over_otp(self.validated_data.get('otp_code'))

    def resend(self):
        self.is_valid(raise_exception=True)
        try:
            record = SmsVerification.objects.get(number='+' + self.validated_data.get('phone'), confirmed=False)
            phone_reconfirmation(record)
            return True
        except SmsVerification.DoesNotExist:
            return False


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['name', 'id']
        extra_kwargs = {
            'name': {'read_only': True},
            'id': {'read_only': True}
        }


class MealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealType
        fields = ['type', 'id']
        extra_kwargs = {
            'type': {'read_only': True},
            'id': {'read_only': True}
        }


class OfferTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferType
        fields = ['type', 'id']
        extra_kwargs = {
            'type': {'read_only': True},
            'id': {'read_only': True}
        }


class RestaurantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantType
        fields = ['type', 'id']
        extra_kwargs = {
            'type': {'read_only': True},
            'id': {'read_only': True}
        }


class MenuSerializer(serializers.ModelSerializer):
    type = MealTypeSerializer()
    offer = OfferTypeSerializer()

    class Meta:
        model = Menu
        fields = ['number', 'name', 'description', 'price', 'image', 'offered_by', 'type', 'offer', 'discount']
        extra_kwargs = {
            'discount': {'required': False}
        }


class MenuForTypeSerializer(serializers.ModelSerializer):
    offer = OfferTypeSerializer()

    class Meta:
        model = Menu
        fields = ['number', 'name', 'description', 'price', 'image', 'offered_by', 'type', 'offer', 'discount']
        extra_kwargs = {
            'discount': {'required': False}
        }


class MealTypesWithMenuSerializer(serializers.ModelSerializer):
    menus = MenuForTypeSerializer(many=True)

    class Meta:
        model = MealType
        fields = ['type', 'id', 'menus']


class RestaurantSerializer(serializers.ModelSerializer):
    from rating.serializers import RestaurantRateSerializer

    cuisines = CuisineSerializer(many=True)
    meal_types = MealTypeSerializer(many=True)
    types = RestaurantTypeSerializer(many=True)
    menus = MenuSerializer(many=True, required=False)
    rate = serializers.SerializerMethodField()
    rates = RestaurantRateSerializer(many=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(RestaurantSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'registre_commerce', 'id_fiscale', 'latitude', 'longitude', 'main_user',
                  'address', 'city', 'cuisines', 'types', 'meal_types', 'menus', 'global_discount', 'on_special_day',
                  'logo', 'open_at', 'close_at', 'rate', 'rates']
        extra_kwargs = {
            'cuisines': {'read_only': True},
            'meal_types': {'read_only': True},
            'types': {'read_only': True},
            'id': {'read_only': True},
            'rate': {'read_only': True},
            'registre_commerce': {'write_only': True},
            'id_fiscale': {'write_only': True},
        }

    def get_rate(self, obj):
        return obj.rates.aggregate(stars_avg=Avg('stars')).get('stars_avg', 0)


class OrderLineSerializer(serializers.ModelSerializer):
    menu_name = serializers.SerializerMethodField()

    def get_menu_name(self, obj):
        return obj.menu.name

    class Meta:
        model = OrderLine
        fields = ['number', 'menu', 'quantity', 'total', 'order', 'menu_name', 'comment']
        extra_kwargs = {
            'menu_name': {'read_only': True},
            'order': {'required': False},
            'comment': {'required': False},
        }


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['number', 'client', 'client_name', 'lines', 'total', 'id', 'restaurant', 'status', 'created_at',
                  'latitude', 'longitude', 'phone', 'address', 'building', 'floor', 'delivery_fees', 'discount_total',
                  'sub_total']
        extra_kwargs = {
            'total': {'read_only': True},
            'number': {'read_only': True},
            'id': {'read_only': True},
            'status': {'read_only': True},
            'created_at': {'read_only': True},
            'delivery_fees': {'read_only': True},
            'discount_total': {'read_only': True},
            'latitude': {'required': False},
            'longitude': {'required': False},
            'phone': {'required': False},
            'address': {'required': False},
            'building': {'required': False},
            'floor': {'required': False}
        }

    def get_client_name(self, obj):
        return obj.client.owner.full_name

    def create(self, validated_data):
        lines = validated_data.pop('lines')
        number = Order.generate_number()
        order = Order.objects.create(number=number, **validated_data)
        for line in lines:
            OrderLine.objects.create(order=order, **line)
        return order


class OrderWRestaurantSerializer(OrderSerializer):
    lines = OrderLineSerializer(many=True, required=False)
    restaurant = RestaurantSerializer(fields=('name', 'logo'))


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'wilaya', 'code_postal']


class WilayaSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = Wilaya
        fields = ['name', 'matricule', 'code_postal', 'cities']

from rest_framework import serializers

from rating.models import RateRestaurant, LikeRestaurant, CommentRestaurant, CommentMenu, LikeMenu, RateMenu, \
    RateDelivery, LikeDelivery, CommentDelivery
from restaurants.serializers import ClientSerializer


class RestaurantRateSerializer(serializers.ModelSerializer):
    # client = ClientSerializer()

    class Meta:
        model = RateRestaurant
        fields = ['id', 'stars', 'comment', 'created_at', 'client', 'restaurant']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class RestaurantLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeRestaurant
        fields = ['restaurant', 'client', 'id', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class RestaurantCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentRestaurant
        fields = ['restaurant', 'client', 'id', 'created_at', 'comment']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class MenuRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateMenu
        fields = ['id', 'stars', 'comment', 'created_at', 'client', 'menu']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class MenuLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeMenu
        fields = ['menu', 'client', 'id', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class MenuCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentMenu
        fields = ['menu', 'client', 'id', 'created_at', 'comment']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class DeliveryRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateDelivery
        fields = ['id', 'stars', 'comment', 'created_at', 'client', 'delivery']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class DeliveryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeDelivery
        fields = ['delivery', 'client', 'id', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }


class DeliveryCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentDelivery
        fields = ['delivery', 'client', 'id', 'created_at', 'comment']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'id': {'read_only': True}
        }

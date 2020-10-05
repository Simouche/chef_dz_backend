from django.db.models import Avg, Sum
from rest_framework import serializers

from base_backend.utils import handle_uploaded_file
from recipe.models import Step, Recipe, IngredientType, Ingredient, QuantityMeasure, Contains, Like, Comment, StarsRate, \
    Participant, CustomContains


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['number', 'description', 'recipe', 'id', 'image']
        extra_kwargs = {
            'recipe': {
                'required': False,
            },
            'id': {
                'read_only': True
            },
            'image': {
                'required': False
            }
        }


class ContainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contains
        fields = ['ingredient', 'quantity', 'id', 'recipe']
        extra_kwargs = {
            'recipe': {
                'required': False,
            },
            'id': {
                'read_only': True
            }
        }


class CustomContainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomContains
        fields = ['ingredient', 'quantity', 'recipe', 'id', 'measure']
        extra_kwargs = {
            'recipe': {
                'required': False,
            },
            'id': {
                'read_only': True
            },
            'measure': {
                'required': False
            },

        }


class RecipeSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, required=False)
    # contains = ContainsSerializer(many=True, required=False)
    custom_contains = CustomContainsSerializer(many=True, required=False)
    images = serializers.ListField(child=serializers.ImageField(), required=False, allow_empty=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()
    stars_avg = serializers.SerializerMethodField()
    stars_sum = serializers.SerializerMethodField()
    cuisine_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    # TODO: add image fields
    class Meta:
        model = Recipe
        fields = ['published_by', 'food_name', 'cost', 'cuisine', 'type', 'description', 'custom_contains', 'steps',
                  'images', 'likes', 'comments', 'stars', 'stars_avg', 'pictures_urls', 'main', 'id',
                  'stars_sum', 'cuisine_name', 'type_name', 'full_name', 'user_id', 'user_image']
        extra_kwargs = {
            'likes': {'read_only': True},
            'comments': {'read_only': True},
            'stars': {'read_only': True},
            'media': {'read_only': True},
            'id': {'read_only': True},
            'stars_avg': {'read_only': True},
            'cuisine_name': {'read_only': True},
            'type_name': {'read_only': True},
            'full_name': {'read_only': True},
            'user_id': {'read_only': True},
            'user_image': {'read_only': True},
        }

    def get_likes(self, obj):
        return obj.likes.count()

    def get_comments(self, obj):
        return obj.comments.count()

    def get_stars(self, obj):
        return obj.stars.count()

    def get_stars_avg(self, obj):
        return obj.stars.aggregate(stars_avg=Avg('stars')).get('stars_avg', 0)

    def get_stars_sum(self, obj):
        return obj.stars.aggregate(stars_sum=Sum('stars')).get('stars_sum')

    def get_full_name(self, obj):
        return obj.published_by.profile.owner.full_name

    def get_cuisine_name(self, obj):
        return obj.cuisine.name

    def get_type_name(self, obj):
        return obj.type.type

    def get_user_id(self, obj):
        return obj.published_by.profile.owner.id

    def get_user_image(self, obj):
        return obj.published_by.profile.owner.get_photo

    def create(self, validated_data):
        steps_data = validated_data.pop('steps') if validated_data.get('steps') else []
        # contains_data = validated_data.pop('contains') if validated_data.get('contains') else []
        custom_contains = validated_data.pop('custom_contains') if validated_data.get('custom_contains') else []
        images = validated_data.pop('images') if validated_data.get('images') else []
        # real_participant = Participant.objects.get(profile__owner__id=validated_data.pop('published_by'))
        recipe = Recipe.objects.create(**validated_data)
        for step in steps_data:
            Step.objects.create(recipe=recipe, **step)
        # for ingredient in contains_data:
        #     Contains.objects.create(recipe=recipe, **ingredient)
        for custom_ingredient in custom_contains:
            CustomContains.objects.create(recipe=recipe, **custom_ingredient)
        for image in images:
            handle_uploaded_file(image, recipe.media + "\\" + image.name)
        return recipe


class IngredientTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientType
        fields = ['type', 'id']
        extra_kwargs = {
            'id': {
                'read_only': True,
            }
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'type', 'measure__name', 'id']
        extra_kwargs = {
            'id': {
                'read_only': True,
            }
        }


class QuantityMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantityMeasure
        fields = ['name']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'recipe', 'created_at', 'id', ]
        extra_kwargs = {
            "created_at": {"required": False, 'read_only': True},
            "id": {"required": False, 'read_only': True}
        }


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    full_name = serializers.CharField(source='user.owner.full_name', read_only=True)
    username = serializers.CharField(source='user.owner.username', read_only=True)
    picture = serializers.CharField(source='user.owner.get_photo', read_only=True)

    class Meta:
        model = Comment
        fields = ['user', 'recipe', 'comment', 'created_at', 'id', 'full_name', 'username', 'picture']
        extra_kwargs = {
            "id": {'read_only': True},
        }


class StarsRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarsRate
        fields = ['user', 'recipe', 'stars', 'created_at', 'id']
        extra_kwargs = {
            "created_at": {"required": False, 'read_only': True},
            "id": {"required": False, 'read_only': True}
        }


class ParticipantSerializer(serializers.ModelSerializer):
    recipes_count = serializers.ReadOnlyField(
        source='recipes.count'
    )
    avg_rate = serializers.SerializerMethodField(read_only=True)
    sum_rate = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    city = serializers.SerializerMethodField(read_only=True)
    wilaya = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    address = serializers.SerializerMethodField(read_only=True)
    photo = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)

    def get_id(self, obj):
        return obj.profile.owner.id

    def get_avg_rate(self, obj):
        return obj.recipes.aggregate(avg=Avg('stars__stars')).get('avg')

    def get_sum_rate(self, obj):
        return obj.recipes.aggregate(sum=Sum('stars__stars')).get('sum')

    def get_full_name(self, obj):
        return obj.profile.owner.full_name

    def get_city(self, obj):
        return obj.profile.owner.lives_in.name if obj.profile.owner.lives_in else 'NP'

    def get_wilaya(self, obj):
        return obj.profile.owner.lives_in.wilaya.name if obj.profile.owner.lives_in else 'NP'

    def get_address(self, obj):
        return obj.profile.owner.address

    def get_photo(self, obj):
        return obj.profile.owner.get_photo

    def get_username(self, obj):
        return obj.profile.owner.username

    class Meta:
        model = Participant
        fields = ['id', 'profile', 'participant_id', 'recipes_count', 'avg_rate', 'full_name', 'city',
                  'sum_rate', 'wilaya', "address", 'photo', 'username']
        extra_kwargs = {
            'participant_id': {'read_only': True},
            'profile': {'write_only': True},
            'id': {'read_only': True},
        }

import os

from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from base_backend.models import BaseModel, do_nothing, cascade
from recipe.utils import generate_participant_code

from restaurant.settings import MEDIA_ROOT, MEDIA_URL, HOST_NAME


class Participant(BaseModel):
    profile = models.OneToOneField('restaurants.Client', on_delete=do_nothing, related_name='profile', unique=True)
    participant_id = models.CharField(max_length=150, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.participant_id = generate_participant_code()
            self.profile.owner.groups.add(Group.objects.get(name='participant'))
        super(Participant, self).save(*args, **kwargs)

    def __str__(self):
        return "{} {} "


class Step(BaseModel):
    number = models.IntegerField()
    description = models.TextField()
    recipe = models.ForeignKey("Recipe", on_delete=cascade, related_name='steps')
    image = models.ImageField(null=True, blank=True, upload_to='step')

    def __str__(self):
        return "step {} of the recipe {}: {}".format(self.number, self.recipe.id, self.recipe.food_name)


class Recipe(BaseModel):
    published_by = models.ForeignKey('Participant', on_delete=do_nothing, blank=True, related_name="recipes")
    food_name = models.CharField(max_length=50)
    cost = models.FloatField()
    description = models.TextField()
    cuisine = models.ForeignKey('restaurants.Cuisine', on_delete=do_nothing, null=True, related_name="recipe_cuisine")
    type = models.ForeignKey('restaurants.MealType', on_delete=do_nothing, null=True, related_name='recipe_type')
    media = models.CharField(max_length=255, unique=True, null=True, blank=True)
    main = models.ImageField(blank=True, null=True, upload_to="recipe/main")

    class Meta:
        unique_together = ('published_by', 'food_name')

    @staticmethod
    def get_media(recipes):
        for i in range(len(recipes)):
            recipes[i].images = []
            images_paths = os.listdir(recipes[i].media)
            for image in images_paths:
                recipes[i].images.append(MEDIA_URL + "recipe/" + str(recipes[i].pk) + "/" + image)
        return recipes

    @property
    def pictures_urls(self):
        images = []
        paths = os.listdir(self.media)
        for path in paths:
            path = path.replace('\\', '%5C', 1) if path.startswith('\\') else path
            images.append(HOST_NAME + MEDIA_URL + "recipe/" + str(self.pk) + "/" + path)
        return images

    @property
    def get_photo(self):
        try:
            return self.main.url
        except ValueError:
            return ""

    def __str__(self):
        return "{} {} belongs to {}".format(self.id, self.food_name, self.published_by.profile.owner.id)


class IngredientType(BaseModel):
    type = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.type


class Ingredient(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    type = models.ForeignKey('IngredientType', on_delete=do_nothing)
    measure = models.ForeignKey('QuantityMeasure', on_delete=do_nothing, null=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.measure.name)


class Contains(BaseModel):
    recipe = models.ForeignKey('Recipe', on_delete=cascade, related_name='contains')
    ingredient = models.ForeignKey('Ingredient', on_delete=do_nothing)
    quantity = models.FloatField()

    def __str__(self):
        return "Recipe {} contains {} ".format(self.recipe.id, self.ingredient.name)


class CustomContains(BaseModel):
    recipe = models.ForeignKey('Recipe', on_delete=cascade, related_name='custom_contains')
    ingredient = models.CharField(max_length=150)
    quantity = models.FloatField()
    measure = models.ForeignKey('QuantityMeasure', on_delete=do_nothing, null=True, blank=True)


class QuantityMeasure(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class BaseRating(BaseModel):
    user = models.ForeignKey('restaurants.Client', on_delete=cascade)
    recipe = models.ForeignKey('Recipe', on_delete=cascade)

    class Meta:
        abstract = True


class Like(BaseRating):
    recipe = models.ForeignKey('Recipe', on_delete=cascade, related_name='likes')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return "the user {} liked the recipe {}".format(self.user.id, self.recipe.id)


class Comment(BaseRating):
    comment = models.TextField()
    recipe = models.ForeignKey('Recipe', on_delete=cascade, related_name='comments')

    def __str__(self):
        return "the user {} commented the recipe {}".format(self.user.id, self.recipe.id)


class StarsRate(BaseRating):
    stars = models.FloatField()
    recipe = models.ForeignKey('Recipe', on_delete=cascade, related_name='stars')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return "the user {} rated the recipe {}".format(self.user.id, self.recipe.id)


@receiver(post_save, sender=Recipe)
def make_recipe_media_directory(instance, *args, **kwargs):
    if not instance.media:
        os.makedirs(os.path.join(MEDIA_ROOT, 'recipe', str(instance.pk)), exist_ok=True)
        # os.makedirs(os.path.join(MEDIA_ROOT, 'step', str(instance.pk)), exist_ok=True)
        instance.media = os.path.join(MEDIA_ROOT, 'recipe', str(instance.pk) + "/")
        instance.save()

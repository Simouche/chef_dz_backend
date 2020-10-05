from django import forms
from django.forms import inlineformset_factory

from recipe.models import Like, Recipe, Comment, Contains, Ingredient, Step, CustomContains, QuantityMeasure
from restaurants.models import Client, Cuisine, MealType
from django.utils.translation import gettext_lazy as _


class LikeForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=Client.objects.all())
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())

    class Meta:
        model = Like
        fields = ['user', 'recipe']


class CommentForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=Client.objects.all())
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Comment")
            }
        )
    )

    class Meta:
        model = Comment
        fields = ['user', 'recipe', 'comment']


class StartRateForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=Client.objects.all())
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())
    stars = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Rate')
            }
        )
    )

    class Meta:
        model = Comment
        fields = ['user', 'recipe', 'stars']


class CreateRecipeForm(forms.ModelForm):
    food_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Recipe Name')
            }
        )
    )
    cost = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Cost')
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _('Description')
            }
        )
    )
    cuisine = forms.ModelChoiceField(
        queryset=Cuisine.objects.all(),
        required=False)
    type = forms.ModelChoiceField(
        queryset=MealType.objects.all(),
        required=False)
    main = forms.ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ['food_name', 'cost', 'description', 'cuisine', 'type', 'main']


class AddRecipeContents(forms.ModelForm):
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all())
    quantity = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Quantity')
            }
        )
    )

    class Meta:
        model = Contains
        fields = ['recipe', 'ingredient', 'quantity']


class AddRecipeCustomContents(forms.ModelForm):
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())
    ingredient = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Ingredient name')
            }
        ))
    quantity = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Quantity')
            }
        )
    )
    measure = forms.ModelChoiceField(queryset=QuantityMeasure.objects.all())

    class Meta:
        model = CustomContains
        fields = ['recipe', 'ingredient', 'quantity', 'measure']


class AddRecipeSteps(forms.ModelForm):
    number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Number')
            }
        )
    )
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Description')
            }
        )
    )
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())

    class Meta:
        model = Step
        fields = ['number', 'description', 'recipe', 'image']


RecipeIngredient = inlineformset_factory(parent_model=Recipe, model=Contains, fields=('ingredient', 'quantity'),
                                         extra=1, can_delete=True)

CustomRecipeIngredient = inlineformset_factory(parent_model=Recipe, model=CustomContains,
                                               fields=('ingredient', 'quantity', 'measure'), extra=1, can_delete=True)

RecipeSteps = inlineformset_factory(parent_model=Recipe, model=Step, fields=('number', 'description', 'image'), extra=1,
                                    can_delete=True)

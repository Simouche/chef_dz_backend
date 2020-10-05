import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Q, Avg, Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView

from base_backend.models import Round
from base_backend.utils import handle_uploaded_file
from recipe.forms import CreateRecipeForm, RecipeSteps, CustomRecipeIngredient
from recipe.models import Participant, Recipe, Ingredient, Like, CustomContains, Step, QuantityMeasure
from restaurant.settings import MEDIA_URL
from restaurants.models import Client


@method_decorator(login_required, name='dispatch')
class GetStatsView(View):
    template_name = ''

    def get(self, request):
        participants = Participant.objects.filter(profile__owner__is_active=True)
        recipes = Recipe.objects.all()
        clients = Client.objects.filter(owner__is_active=True)

        participant_count = participants.count()
        recipe_count = recipes.count()
        clients_count = clients.count()
        participants_rate = float(participant_count) / float(clients_count) * 100.0
        ranking = participants.aggregate(stars=Sum('recipes__starsrate__stars')).order_by('-stars')

        context = dict(participant_count=participant_count, participants=participants,
                       participants_rate=participants_rate, recipes=recipes, clients=clients,
                       clients_count=clients_count, recipe_count=recipe_count, ranking=ranking)

        return render(request, template_name=self.template_name, context=context)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('recipe.view_recipe'), name='dispatch')
class RecipesListView(ListView):
    model = Recipe
    context_object_name = "recipes"
    allow_empty = True
    ordering = '-created_at'
    paginate_by = 40
    template_name = 'view_recipe_owner.html'

    def get_queryset(self):
        if self.kwargs.get('pk', None):
            query = Q(published_by_id=self.kwargs.get('pk', 0),
                      published_by__profile__owner__is_active=True)
        else:
            query = Q(published_by__profile__owner__is_active=True)
        return Recipe.objects.filter(query).annotate(avg=Round(Avg('stars__stars'), 1)).annotate(
            likes_=Count('likes')).annotate(comments_=Count('comments')).order_by('-created_at')


@method_decorator(login_required, name='dispatch')
class RecipeUpdateView(UpdateView):
    model = Recipe
    fields = ['food_name', 'cost', 'description', 'cuisine', 'type', 'main']
    template_name = 'updaterecipe.html'
    context_object_name = 'recipe'
    success_url = reverse_lazy('recipe:recipes')

    def get_queryset(self):
        return Recipe.objects.filter(published_by=self.request.user.client.participant,
                                     published_by__profile__owner__is_active=True)


@method_decorator(login_required, name='dispatch')
class RecipeDeleteView(DeleteView):
    model = Recipe
    success_url = reverse_lazy('recipe:recipes')
    context_object_name = 'recipe'

    def get_queryset(self):
        return Recipe.objects.filter(published_by=self.request.user.client.participant,
                                     published_by__profile__owner__is_active=True)


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'view_recipe.html'
    context_object_name = 'recipe'
    queryset = Recipe.objects.filter(published_by__profile__owner__is_active=True)

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        try:
            query = Q(user=self.request.user.client)
        except AttributeError:
            query = ~Q(user=None)
        context['liked'] = self.get_object().likes.filter(query).exists()
        context['rate'] = self.get_object().stars.filter(query).values_list('stars')
        context['avg'] = self.get_object().stars.aggregate(avg=Round(Avg('stars'), 1)).get('avg', 0)
        context['other'] = self.queryset.filter(published_by=self.get_object().published_by) \
            .annotate(avg=Round(Avg('stars__stars'), 1)) \
            .annotate(likes_=Count('likes'))
        context['user_avg'] = Participant.objects.filter(pk=self.get_object().published_by.pk).annotate(
            avg=Round(Avg('recipes__stars__stars'), 1)).annotate(likes_=Count('recipes__likes'))[0]
        context['measures'] = QuantityMeasure.objects.all()
        return context

    # def get_object(self, queryset=None):
    #     """
    #            Return the object the view is displaying.
    #
    #            Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
    #            Subclasses can override this to return any object.
    #            """
    #     # Use a custom queryset if provided; this is required for subclasses
    #     # like DateDetailView
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #
    #     # Next, try looking up by primary key.
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #     slug = self.kwargs.get(self.slug_url_kwarg)
    #     if pk is not None:
    #         queryset = queryset.filter(pk=pk)
    #
    #     # Next, try looking up by slug.
    #     if slug is not None and (pk is None or self.query_pk_and_slug):
    #         slug_field = self.get_slug_field()
    #         queryset = queryset.filter(**{slug_field: slug})
    #
    #     # If none of those are defined, it's an error.
    #     if pk is None and slug is None:
    #         raise AttributeError(
    #             "Generic detail view %s must be called with either an object "
    #             "pk or a slug in the URLconf." % self.__class__.__name__
    #         )
    #
    #     try:
    #         # Get the single item from the filtered queryset
    #         obj = queryset.get()
    #         obj.images = []
    #         images_paths = os.listdir(obj.media)
    #         for image in images_paths:
    #             obj.images.append(MEDIA_URL + "recipe/" + str(obj.pk) + "/" + image)
    #     except queryset.model.DoesNotExist:
    #         raise Http404(_("No %(verbose_name)s found matching the query") %
    #                       {'verbose_name': queryset.model._meta.verbose_name})
    #     return obj


class IngredientsListView(ListView):
    model = Ingredient
    context_object_name = "ingredients"
    template_name = ''


@method_decorator(login_required, name='dispatch')
class IngredientCreateView(CreateView):
    model = Ingredient
    fields = ['name', 'type', 'measure']
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''


@method_decorator(login_required, name='dispatch')
class IngredientUpdateView(UpdateView):
    model = Ingredient
    fields = ['name', 'type', 'measure']
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''


@method_decorator(login_required, name='dispatch')
class IngredientDeleteView(DeleteView):
    model = Ingredient
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''


class StepsListView(ListView):
    model = Step
    context_object_name = "ingredients"
    template_name = ''

    def get_queryset(self):
        return Step.objects.filter(recipe_id=self.kwargs.get('pkr'))


@method_decorator(login_required, name='dispatch')
class StepCreateView(CreateView):
    model = Step
    fields = ['number', 'description', 'recipe', 'image']
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-update', self.get_object().recipe.pk)


@method_decorator(login_required, name='dispatch')
class StepUpdateView(UpdateView):
    model = Step
    fields = ['number', 'description', 'recipe', 'image']
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-update', self.get_object().recipe.pk)


@method_decorator(login_required, name='dispatch')
class StepDeleteView(DeleteView):
    model = Step
    success_url = reverse_lazy('recipe:ingredients')
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-update', self.get_object().recipe.pk)


class CustomIngredientListView(ListView):
    model = CustomContains
    context_object_name = "ingredients"
    template_name = ''
    ordering = 'created_at'

    def get_queryset(self):
        return CustomContains.objects.filter(recipe_id=self.kwargs.get('pkr'))


class CustomIngredientCreateView(CreateView):
    model = CustomContains
    fields = ['recipe', 'ingredient', 'quantity', 'measure']
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-update', self.get_object().recipe.pk)


@method_decorator(login_required, name='dispatch')
class CustomIngredientUpdateView(UpdateView):
    model = CustomContains
    fields = ['recipe', 'ingredient', 'quantity', 'measure']
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-details', self.get_object().recipe.pk)


class CustomIngredientDeleteView(DeleteView):
    model = CustomContains
    template_name = ''

    def get_success_url(self):
        return reverse_lazy('recipe:recipe-update', self.get_object().recipe.pk)


# @method_decorator(login_required, name='dispatch')
# class ParticipantList(ListView):
#     model = Participant
#     context_object_name = "participants"
#     template_name = ''
#
#     def get_queryset(self):
#         return Participant.objects.filter(profile__owner__is_active=True).order_by('profile__owner__date_joined')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('recipe.add_recipe', ), name='dispatch')
class RecipeCreate(View):
    template_name = 'addrecipe.html'

    def prepare_args(self, pk=None, request=None):
        if pk:
            self.title = _('Update Recipe')
            instance = get_object_or_404(Recipe, pk=pk)
            if request.method == 'GET':
                self.recipe_form = CreateRecipeForm(instance=instance)
                self.ingredients_form = CustomRecipeIngredient(instance=instance)
                self.steps_form = RecipeSteps(instance=instance)
            else:
                self.recipe_form = CreateRecipeForm(instance=instance, data=request.POST, files=request.FILES)
                self.ingredients_form = CustomRecipeIngredient(instance=instance, data=request.POST)
                self.steps_form = RecipeSteps(instance=instance, data=request.POST, files=request.FILES)
        else:
            self.title = _('Create Recipe')
            if request.method == 'POST':
                self.recipe_form = CreateRecipeForm(initial={'published_by': self.request.user.client.participant},
                                                    data=request.POST, files=request.FILES)
                self.ingredients_form = CustomRecipeIngredient(request.POST)
                self.steps_form = RecipeSteps(request.POST, request.FILES)
            else:
                self.recipe_form = CreateRecipeForm(initial={'published_by': self.request.user.client.participant})
                self.ingredients_form = CustomRecipeIngredient()
                self.steps_form = RecipeSteps()

    def get(self, request, pk=None):
        self.prepare_args(pk, request)
        context = dict(title=self.title, recipe_form=self.recipe_form, ingredients_form=self.ingredients_form,
                       steps_form=self.steps_form)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, pk=None):
        self.prepare_args(pk, request=request)
        if self.recipe_form.is_valid():
            recipe = self.recipe_form.save(commit=False)
            recipe.published_by = request.user.client.participant
            recipe.save()
            images = request.FILES.getlist('media')
            for image in images:
                handle_uploaded_file(image, recipe.media + image.name)
            if self.ingredients_form.is_valid():
                self.ingredients_form.instance = recipe
                self.ingredients_form.save()
            else:
                recipe.delete()
                context = dict(title=self.title, recipe_form=self.recipe_form, ingredients_form=self.ingredients_form,
                               steps_form=self.steps_form)
                return render(request, template_name=self.template_name, context=context)
            if self.steps_form.is_valid():
                self.steps_form.instance = recipe
                self.steps_form.save()
            else:
                recipe.contains.delete()
                recipe.delete()
                context = dict(title=self.title, recipe_form=self.recipe_form, ingredients_form=self.ingredients_form,
                               steps_form=self.steps_form)
                return render(request, template_name=self.template_name, context=context)
            messages.success(request, _('Success'))
            return redirect('recipe:recipes')
        else:
            context = dict(title=self.title, recipe_form=self.recipe_form, ingredients_form=self.ingredients_form,
                           steps_form=self.steps_form)
            return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LikeView(CreateView):
    model = Like
    fields = ['recipe', 'user']
    pass


@method_decorator(login_required, name='dispatch')
class ParticipantsListView(ListView):
    model = Participant
    context_object_name = "participants"
    template_name = 'rank.html'
    queryset = Participant.objects.all().annotate(avg=Round(Avg('recipes__stars__stars'), 1)) \
        .annotate(likes=Count('recipes__likes')).annotate(stars_sum=Sum('recipes__stars__stars'))
    ordering = '-stars_sum'


@method_decorator(login_required, name='dispatch')
class CreateParticipantView(View):

    def get(self, request, *args, **kwargs):
        if request.user.client.participant is None:
            request.user.client.participant = Participant.objects.create(profile=request.user.client)
            request.user.client.save()
        return redirect('recipe:recipe-create')

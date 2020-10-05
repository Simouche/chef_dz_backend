from django.db.models import Avg, Sum
from django.shortcuts import get_list_or_404
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from base_backend import permissions as my_perms
from recipe.models import Step, Recipe, IngredientType, Ingredient, QuantityMeasure, Like, Comment, StarsRate, Contains, \
    Participant, CustomContains
from recipe.serializers import StepSerializer, RecipeSerializer, IngredientTypeSerializer, IngredientSerializer, \
    QuantityMeasureSerializer, LikeSerializer, CommentSerializer, StarsRateSerializer, ContainsSerializer, \
    ParticipantSerializer, CustomContainsSerializer


class StepViewSet(ModelViewSet):
    serializer_class = StepSerializer
    queryset = Step.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        if self.action == 'retrieve':
            """
            Returns the list of steps of the recipe the view is displaying.
            """
            self.lookup_field = 'recipe_id'
            queryset = self.filter_queryset(self.get_queryset())

            # Perform the lookup filtering.
            lookup_url_kwarg = 'pk'  # bad hard coding! very bad!

            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_list_or_404(queryset, **filter_kwargs)

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            return obj
        else:
            return super(StepViewSet, self).get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    def get_serializer(self, many=True, *args, **kwargs):
        if isinstance(self.request.data, list):
            return super(StepViewSet, self).get_serializer(many=many, *args, **kwargs)
        return super(StepViewSet, self).get_serializer(many=False, *args, **kwargs)


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        request.data['published_by'] = Participant.objects.get(profile__owner__id=request.data['published_by']).pk
        return super(RecipeViewSet, self).create(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.query_params.get('user', None):
            user_id = self.request.query_params.get('user', None)
            try:
                participant = Participant.objects.get(profile__owner_id=user_id)
            except Participant.DoesNotExist:
                participant = None
            self.queryset = self.queryset.filter(published_by=participant)
        return super(RecipeViewSet, self).get_queryset()


class IngredientTypeViewSet(ModelViewSet):
    serializer_class = IngredientTypeSerializer
    queryset = IngredientType.objects.all()
    permission_classes = [my_perms.IsReadOnly]


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [my_perms.IsReadOnly]


class QuantityViewSet(ModelViewSet):
    serializer_class = QuantityMeasureSerializer
    queryset = QuantityMeasure.objects.all()
    permission_classes = [my_perms.IsReadOnly]


class ContainsViewSet(ModelViewSet):
    serializer_class = ContainsSerializer
    queryset = Contains.objects.all()
    permission_classes = [permissions.AllowAny]  # TODO: change back

    def get_serializer(self, many=True, *args, **kwargs):
        if isinstance(self.request.data, list):
            return super(ContainsViewSet, self).get_serializer(many=many, *args, **kwargs)
        return super(ContainsViewSet, self).get_serializer(many=False, *args, **kwargs)

    def get_object(self):
        if self.action == 'retrieve':
            """
            Returns the list of steps of the recipe the view is displaying.
            """
            self.lookup_field = 'recipe_id'
            queryset = self.filter_queryset(self.get_queryset())

            # Perform the lookup filtering.
            lookup_url_kwarg = 'pk'  # bad hard coding! very bad!

            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_list_or_404(queryset, **filter_kwargs)

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            return obj
        else:
            return super(ContainsViewSet, self).get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class CustomContainsViewSet(ModelViewSet):
    serializer_class = CustomContainsSerializer
    queryset = CustomContains.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer(self, many=True, *args, **kwargs):
        if isinstance(self.request.data, list):
            return super(CustomContainsViewSet, self).get_serializer(many=many, *args, **kwargs)
        return super(CustomContainsViewSet, self).get_serializer(many=False, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def filter(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        recipe_id = request.GET.get('recipe', 0)
        data = query_set.filter(recipe_id=recipe_id)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


class LikeViewSet(ModelViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            recipe = self.request.query_params.get('recipe', None)
            user = self.request.query_params.get('user', None)
            if recipe and recipe.isnumeric():
                return Like.objects.filter(recipe_id=int(recipe))
            elif user and user.isnumeric():
                return Like.objects.filter(user_id=int(user))
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['user'] = request.user.client.pk
        request._full_data = data
        return super(LikeViewSet, self).create(request, *args, **kwargs)

    @action(methods=['GET'], detail=False, url_path="check-like", permission_classes=[permissions.IsAuthenticated])
    def check_like(self, request, *args, **kwargs):
        recipe_id = request.query_params.get('recipe', None)
        exists = Recipe.objects.filter(likes__user=request.user.client, id=recipe_id).exists()
        return Response({"liked": exists})

    @action(methods=['DELETE'], detail=False, url_path="delete-like", permission_classes=[permissions.IsAuthenticated])
    def delete_like(self, request, *args, **kwargs):
        recipe_id = self.request.query_params.get('recipe', 0)
        user_id = self.request.query_params.get('user', 0)
        obj = get_object_or_404(self.queryset, recipe_id=recipe_id, user__owner_id=user_id)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            recipe = self.request.query_params.get('recipe', None)
            if recipe and recipe.isnumeric():
                return Comment.objects.filter(recipe_id=int(recipe))
            else:
                user = self.request.user
                return Comment.objects.filter(user_id=user.client.pk)

        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['user'] = request.user.client.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StarsRateViewSet(ModelViewSet):
    serializer_class = StarsRateSerializer
    queryset = StarsRate.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            recipe = self.request.query_params.get('recipe', None)
            if recipe and recipe.isnumeric():
                return StarsRate.objects.filter(recipe_id=int(recipe))
            else:
                user = self.request.user
                return StarsRate.objects.filter(user_id=user.client.pk)
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['user'] = request.user.client.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ParticipantViewSet(ModelViewSet):
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.all().annotate(avg=Avg('recipes__stars__stars')) \
        .annotate(sum=Sum('recipes__stars__stars')).order_by('-sum')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

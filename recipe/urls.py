from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views
from . import apis

app_name = 'recipe'

api_router = SimpleRouter()
api_router.register('steps', apis.StepViewSet, basename='steps')
api_router.register('recipes/contain', apis.CustomContainsViewSet,
                    basename='recipe-contain')  # TODO: change back to contains viewset
api_router.register('recipes/custom-contain', apis.CustomContainsViewSet, basename='recipe-custom-contain')
api_router.register('recipes', apis.RecipeViewSet, basename='recipes')
api_router.register('ingredient/type', apis.IngredientTypeViewSet, basename='ingredient-types')
api_router.register('ingredient/quantity', apis.QuantityViewSet, basename='ingredient-quantities')
api_router.register('ingredient', apis.IngredientViewSet, basename='ingredients')
api_router.register('rating/like', apis.LikeViewSet, basename='likes')
api_router.register('rating/comment', apis.CommentViewSet, basename='comments')
api_router.register('rating/stars', apis.StarsRateViewSet, basename='stars')
api_router.register('participants', apis.ParticipantViewSet, basename='participants')

extra_urls = []

urlpatterns = [
    # views urls
    path('stats/', views.GetStatsView.as_view(), name='stats'),
    path('recipes/', views.RecipesListView.as_view(), name='recipes'),
    path('recipes/<int:pk>/', views.RecipesListView.as_view(), name='user-recipes'),
    path('recipes/create/', views.RecipeCreate.as_view(), name='recipe-create'),
    path('recipes/create/<int:pk>/', views.RecipeCreate.as_view(), name='recipe-update-1'),
    path('recipes/<int:pk>/details/', views.RecipeDetailView.as_view(), name='recipe-details'),
    path('recipes/<int:pk>/update/', views.RecipeUpdateView.as_view(), name='recipe-update'),
    path('recipes/<int:pkr>/update/custom-ingredients/', views.CustomIngredientListView.as_view(),
         name='recipe-update-list-ingredients'),
    path('recipes/<int:pkr>/update/custom-ingredients/create/', views.CustomIngredientCreateView.as_view(),
         name='recipe-update-ingredient-create'),
    path('recipes/<int:pkr>/update/custom-ingredients/update/<int:pk>/', views.CustomIngredientUpdateView.as_view(),
         name='recipe-update-ingredient-update'),
    path('recipes/<int:pkr>/update/custom-ingredients/delete/<int:pk>/', views.CustomIngredientDeleteView.as_view(),
         name='recipe-update-ingredient-delete'),
    path('recipes/<int:pkr>/update/steps/', views.StepsListView.as_view(), name='recipe-update-steps-list'),
    path('recipes/<int:pkr>/update/steps/create/', views.StepCreateView.as_view(), name='recipe-update-steps-create'),
    path('recipes/<int:pkr>/update/steps/update/<int:pk>/', views.StepUpdateView.as_view(),
         name='recipe-update-steps-update'),
    path('recipes/<int:pkr>/update/steps/delete/<int:pk>/', views.StepDeleteView.as_view(),
         name='recipe-update-steps-delete'),
    path('recipes/<int:pk>/delete/', views.RecipeDetailView.as_view(), name='recipe-delete'),
    path('ingredients/', views.IngredientsListView.as_view(), name='ingredients'),
    path('participants/', views.ParticipantsListView.as_view(), name='participant'),
    path('participants/participate/', views.CreateParticipantView.as_view(), name='participante-create'),

    # api urls
    path('api/', include(extra_urls + api_router.urls)),
]

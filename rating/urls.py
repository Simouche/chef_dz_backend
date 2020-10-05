from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views
from . import apis

app_name = 'rating'

api_router = SimpleRouter()
api_router.register('likes/restaurant', apis.LikeRestaurantViewSet, basename='like-restaurant')
api_router.register('likes/menu', apis.LikeMenuViewSet, basename='like-menu')
api_router.register('likes/delivery', apis.LikeDeliveryViewSet, basename='like-delivery')
api_router.register('comments/restaurant', apis.CommentRestaurantViewSet, basename='comment-restaurant')
api_router.register('comments/menu', apis.CommentMenuViewSet, basename='comment-menu')
api_router.register('comments/delivery', apis.CommentDeliveryViewSet, basename='comment-delivery')
api_router.register('rate/restaurant', apis.RateRestaurantViewSet, basename='rate-restaurant')
api_router.register('rate/menu', apis.RateMenuViewSet, basename='rate-menu')
api_router.register('rate/delivery', apis.RateDeliveryViewSet, basename='rate-delivery')

extra_urls = []

urlpatterns = [
    # api urls
    path('api/', include(extra_urls + api_router.urls)),
]

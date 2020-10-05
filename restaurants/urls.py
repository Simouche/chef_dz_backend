from django.conf import settings
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views
from . import apis

app_name = 'restaurants'

api_router = SimpleRouter()
api_router.register('users', apis.UserViewSet, basename='users')
api_router.register('cuisines', apis.CuisineViewSet, basename='cuisines')
api_router.register('meal-types', apis.MealTypeViewSet, basename='meals-types')
api_router.register('restaurant-types', apis.RestaurantTypeViewSet, basename='restaurants-types')
api_router.register('restaurants', apis.RestaurantViewSet, basename='restaurants')
api_router.register('menus', apis.MenuViewSet, basename='menus')
api_router.register('orders', apis.OrderViewSet, basename='orders')
api_router.register('orders/lines', apis.OrderLineViewSet, basename='orders-lines')
api_router.register('wilayas', apis.WilayaViewSet, basename='wilayas')
api_router.register('cities', apis.CityViewSet, basename='cities')
api_router.register('address', apis.AddressViewSet, basename='address')
api_router.register('phone', apis.PhoneViewSet, basename='phone')

extra_urls = [
    path('login/', apis.LoginApi.as_view()),
    path('otp/', apis.OtpApi.as_view()),
    path('version/', apis.version),
]
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('verification/otp/', views.VerificationOTPView.as_view(), name='verification-otp'),
    path('coming_soon/', views.coming_soon.as_view(), name='coming_soon'),
    path('restaurant/menu/all/', views.MenuListView.as_view(), name='list-menu'),
    path('restaurant/menu/<int:pk>/all/', views.MenuListView.as_view(), name='list-restaurant-menu'),
    path('restaurant/menu/<int:pk>/search/', views.MenuSearchListView.as_view(), name='search-restaurant-menu'),
    path('restaurant/menu/create/', views.MenuCreateView.as_view(), name='create-menu'),
    path('restaurant/menu/<int:pk>/update/', views.MenuUpdateView.as_view(), name='update-menu'),
    path('restaurant/menu/<int:pk>/details/', views.MenuDetailsView.as_view(), name='details-menu'),
    path('restaurant/menu/<int:pk>/delete/', views.MenuDeleteView.as_view(), name='delete-menu'),
    path('restaurant/restaurants/all/', views.RestaurantListView.as_view(), name='list-restaurant'),
    path('restaurant/restaurants/create/', views.RestaurantCreateView.as_view(), name='create-restaurant'),
    path('restaurant/restaurants/list-and-search/', views.RestaurantsSearchList.as_view(), name='search-restaurant'),
    path('restaurant/restaurants/<int:pk>/update/', views.RestaurantUpdateView.as_view(), name='update-restaurant'),
    path('restaurant/restaurants/<int:pk>/details/', views.RestaurantDetailsView.as_view(), name='details-restaurant'),
    path('restaurant/restaurants/<int:pk>/delete/', views.RestaurantDeleteView.as_view(), name='delete-restaurant'),
    path('restaurant/orders/all/', views.OrderListView.as_view(), name='list-order'),
    path('restaurant/orders/create/', views.OrderCreateView.as_view(), name='create-order'),
    path('restaurant/orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='update-order'),
    path('restaurant/orders/<int:pk>/line/update/', views.OrderLineUpdateView.as_view(), name='update-order-line'),
    path('restaurant/orders/<int:pk>/details/', views.OrderDetailsView.as_view(), name='details-order'),
    path('restaurant/orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='delete-order'),
    path('restaurant/orders/<int:pk>/line/delete/', views.OrderLineDeleteView.as_view(), name='delete-order-line'),
    path('restaurant/offers-types/create/', views.RestaurantOfferTypeCreate.as_view(), name='create-offer-type'),
    path('restaurant/offers-types/all/', views.RestaurantOfferList.as_view(), name='list-offer-type'),
    path('restaurant/meals-types/all/', views.RestaurantMealList.as_view(), name='list-meal-type'),
    path('restaurant/meals-types/create/', views.RestaurantMealCreate.as_view(), name='create-meal-type'),
    path('restaurant/cuisines/create/', views.RestaurantCuisineCreate.as_view(), name='create-cuisine'),
    path('restaurant/cuisines/all/', views.RestaurantCuisinesList.as_view(), name='list-cuisine'),
    path('restaurant/restaurants-types/create/', views.RestaurantTypeCreate.as_view(), name='create-restaurant-type'),
    path('restaurant/restaurants-types/all/', views.RestaurantTypesList.as_view(), name='list-restaurant-type'),

    # api urls
    path('api/', include(extra_urls + api_router.urls)),
]

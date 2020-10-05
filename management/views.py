from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from delivery.models import DeliveryGuy
from restaurants.models import User, Client, Restaurant


@method_decorator(login_required(), name='dispatch')
class UserList(ListView):
    template_name = ''
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('-date_joined')


@method_decorator(login_required(), name='dispatch')
class ClientList(ListView):
    template_name = ''
    model = Client
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(owner__is_active=True).order_by('-date_joined')


@method_decorator(login_required(), name='dispatch')
class RestaurantList(ListView):
    template_name = ''
    model = Restaurant
    context_object_name = 'restaurants'

    def get_queryset(self):
        return Restaurant.objects.filter(main_user__is_active=True)


class DeliveryGuyList(ListView):
    template_name = ''
    model = DeliveryGuy
    context_object_name = 'guys'

    def get_queryset(self):
        return DeliveryGuy.objects.filter(owner__is_active=True)

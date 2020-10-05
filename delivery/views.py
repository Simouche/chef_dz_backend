from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView

from delivery.models import Delivery


class DeliveryCreateView(CreateView):
    model = Delivery
    success_url = ""  # TODO: reverse this
    template_name = ""
    pass


class DeliveryUpdateView(UpdateView):
    model = Delivery
    success_url = ""  # TODO: reverse this
    template_name = ""
    pass


class DeliveryDeleteView(DeleteView):
    model = Delivery
    success_url = ""  # TODO: reverse this
    template_name = ""
    pass


class DeliveryTracksView:
    pass
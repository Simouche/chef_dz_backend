from django.db import models
from django.utils.translation import gettext_lazy as _

from base_backend.models import BaseModel, do_nothing, DeletableModel


class DeliveryGuy(BaseModel):
    owner = models.OneToOneField('restaurants.User', on_delete=models.DO_NOTHING, related_name='delivery_guy')
    vehicle = models.ForeignKey('VehicleType', on_delete=do_nothing)


class VehicleType(BaseModel):
    type = models.CharField(max_length=30, unique=True)


class Delivery(DeletableModel):
    STATUS = (('P', _('Pending')), ('A', _('Accepted')), ('P', _('Picked')), ('D', _('Delivered')))

    status = models.CharField(max_length=2, choices=STATUS, default='P')
    order = models.ForeignKey('restaurants.Order', on_delete=do_nothing)
    delivered_by = models.ForeignKey('DeliveryGuy', on_delete=do_nothing)
    address = models.ForeignKey('restaurants.Address', on_delete=do_nothing, null=True, blank=True)


class DeliveryTracks(BaseModel):
    latitude = models.FloatField()
    longitude = models.FloatField()
    delivery = models.ForeignKey('Delivery', on_delete=do_nothing)

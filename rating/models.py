from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver

from base_backend.messaging import notify_user
from base_backend.models import BaseModel, do_nothing


class AbstractBaseReview(BaseModel):
    client = models.ForeignKey('restaurants.Client', on_delete=do_nothing)

    class Meta:
        abstract = True


class BaseComment(AbstractBaseReview):
    comment = models.CharField(max_length=255)

    class Meta:
        abstract = True


class AbstractBaseRate(BaseComment):
    stars = models.FloatField(default=0)
    comment = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class BaseLike(AbstractBaseReview):
    class Meta:
        abstract = True

    pass


class BaseDeliveryReviews:
    delivery = models.ForeignKey('delivery.DeliveryGuy', on_delete=do_nothing, related_name="reviews")

    class Meta:
        abstract = True


class BaseMenuReviews:
    menu = models.ForeignKey('restaurants.Menu', on_delete=do_nothing, related_name="reviews")

    class Meta:
        abstract = True


class BaseRestaurantReviews:
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=do_nothing, related_name="reviews")

    class Meta:
        abstract = True


class RateDelivery(AbstractBaseRate, BaseDeliveryReviews):
    delivery = models.ForeignKey('delivery.DeliveryGuy', on_delete=do_nothing, related_name="rates")


class RateRestaurant(AbstractBaseRate, BaseRestaurantReviews):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=do_nothing, related_name="rates")


class RateMenu(AbstractBaseRate, BaseMenuReviews):
    menu = models.ForeignKey('restaurants.Menu', on_delete=do_nothing, related_name="rates")


class CommentDelivery(BaseComment, BaseDeliveryReviews):
    delivery = models.ForeignKey('delivery.DeliveryGuy', on_delete=do_nothing, related_name="comments")


class CommentRestaurant(BaseComment, BaseRestaurantReviews):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=do_nothing, related_name="comments")


class CommentMenu(BaseComment, BaseMenuReviews):
    menu = models.ForeignKey('restaurants.Menu', on_delete=do_nothing, related_name="comment")


class LikeDelivery(BaseLike, BaseDeliveryReviews):
    delivery = models.ForeignKey('delivery.DeliveryGuy', on_delete=do_nothing, related_name="likes")


class LikeRestaurant(BaseLike, BaseRestaurantReviews):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=do_nothing, related_name="likes")


class LikeMenu(BaseLike, BaseMenuReviews):
    menu = models.ForeignKey('restaurants.Menu', on_delete=do_nothing, related_name="likes")


@receiver(post_save, sender=CommentRestaurant)
def notify_restaurant_comment(sender, instance, created, raw, **kwargs):
    if created:
        notify_user(instance.restaurant.owner.notification_token,
                    {'title': 'New comment', 'message': 'Someone commented on your restaurant'})


@receiver(post_save, sender=CommentDelivery)
def notify_delivery_comment(sender, instance, created, raw, **kwargs):
    if created:
        notify_user(instance.delivery.owner.notification_token,
                    {'title': 'New comment', 'message': 'Someone commented on your restaurant'})
    pass


@receiver(post_save, sender=CommentMenu)
def notify_menu_comment(sender, instance, created, raw, **kwargs):
    if created:
        notify_user(instance.menu.offered_by.owner.notification_token,
                    {'title': 'New comment', 'message': 'Someone commented on your restaurant'})
    pass
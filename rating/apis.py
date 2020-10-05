from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from base_backend.utils import RequestDataFixer
from rating.models import CommentRestaurant, RateRestaurant, LikeRestaurant, CommentMenu, RateMenu, LikeMenu, \
    CommentDelivery, RateDelivery, LikeDelivery
from rating.serializers import RestaurantCommentSerializer, RestaurantRateSerializer, RestaurantLikeSerializer, \
    MenuCommentSerializer, MenuRateSerializer, MenuLikeSerializer, DeliveryCommentSerializer, DeliveryRateSerializer, \
    DeliveryLikeSerializer


class CommentRestaurantViewSet(ModelViewSet):
    serializer_class = RestaurantCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = CommentRestaurant.objects.all()

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(CommentRestaurantViewSet, self).create(fixer, *args, **kwargs)


class RateRestaurantViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RestaurantRateSerializer
    queryset = RateRestaurant.objects.all()

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(RateRestaurantViewSet, self).create(fixer, *args, **kwargs)


class LikeRestaurantViewSet(ModelViewSet):
    serializer_class = RestaurantLikeSerializer
    queryset = LikeRestaurant.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(LikeRestaurantViewSet, self).create(fixer, *args, **kwargs)


class CommentMenuViewSet(ModelViewSet):
    serializer_class = MenuCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = CommentMenu.objects.all()

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(CommentMenuViewSet, self).create(fixer, *args, **kwargs)


class RateMenuViewSet(ModelViewSet):
    serializer_class = MenuRateSerializer
    queryset = RateMenu.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(RateMenuViewSet, self).create(fixer, *args, **kwargs)


class LikeMenuViewSet(ModelViewSet):
    queryset = LikeMenu.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = MenuLikeSerializer

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(LikeMenuViewSet, self).create(fixer, *args, **kwargs)


class CommentDeliveryViewSet(ModelViewSet):
    serializer_class = DeliveryCommentSerializer
    queryset = CommentDelivery.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(CommentDeliveryViewSet, self).create(fixer, *args, **kwargs)


class RateDeliveryViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = RateDelivery.objects.all()
    serializer_class = DeliveryRateSerializer

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(RateDeliveryViewSet, self).create(fixer, *args, **kwargs)


class LikeDeliveryViewSet(ModelViewSet):
    serializer_class = DeliveryLikeSerializer
    queryset = LikeDelivery.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(LikeDeliveryViewSet, self).create(fixer, *args, **kwargs)

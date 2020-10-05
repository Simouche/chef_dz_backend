from django.db.models import Q, Avg
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from base_backend import permissions as my_perms
from base_backend.utils import RequestDataFixer
from restaurants.models import User, Cuisine, MealType, AppVersion, RestaurantType, Restaurant, Menu, Order, OrderLine, \
    Wilaya, City, Address, Phone
from restaurants.serializers import UserSerializer, SmsConfirmationSerializer, CuisineSerializer, \
    RestaurantTypeSerializer, RestaurantSerializer, MenuSerializer, OrderLineSerializer, WilayaSerializer, \
    CitySerializer, OrderWRestaurantSerializer, MealTypesWithMenuSerializer, MealTypeSerializer, OrderSerializer, \
    AddressSerializer, PhoneSerializer


class LoginApi(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context=dict(request=request))
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            dict(
                token=token.key,
                user_id=user.pk,
                phone=user.phone,
                email=user.email,
                type=user.user_type,
                photo=user.photo.url if user.photo else None,
                address=user.address,
                city=user.lives_in_id,
                birth_date=user.birth_date,
                username=user.username,
                # is_participant=user.client.is_participant if user.client is not None else None,
                # participant_id=user.client.participant.participant_id if user.client else None,
            )
        )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action == 'create' or self.action == 'register':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticatedOrReadOnly()]

    @action(methods=['post'], detail=False, url_path='register', permission_classes=[permissions.AllowAny()])
    def register(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response:
            response.data = dict(status=True, code=4)
        return response

    def create(self, request, *args, **kwargs):
        return self.register(request, *args, **kwargs)


class OtpApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = SmsConfirmationSerializer(data=request.GET)
        result = serializer.resend()
        if result:
            response = dict(status=True, code=5)
        else:
            response = dict(status=False, code=21)
        return Response(response)

    def put(self, request):
        serializer = SmsConfirmationSerializer(data=request.data)
        result = serializer.activate()
        if result:
            response = dict(status=True, code=5)
        else:
            response = dict(status=False, code=20)
        return Response(response)


class CuisineViewSet(ModelViewSet):
    serializer_class = CuisineSerializer
    permission_classes = [my_perms.IsAdminOrReadOnly]
    queryset = Cuisine.objects.all()


class MealTypeViewSet(ModelViewSet):
    permission_classes = [my_perms.IsAdminOrReadOnly]
    serializer_class = MealTypeSerializer
    queryset = MealType.objects.all()

    def get_serializer(self, *args, **kwargs):
        if self.action == "get_types_with_menus":
            serializer_class = MealTypesWithMenuSerializer
            kwargs['context'] = self.get_serializer_context()
            return serializer_class(*args, **kwargs)
        return super(MealTypeViewSet, self).get_serializer(*args, **kwargs)

    @action(['get'], detail=False, url_path="type-with-menus", )
    def get_types_with_menus(self, request, *args, **kwargs):
        types = self.get_queryset().filter(menus__offered_by=request.query_params.get('restaurant', 0))
        types = self.get_serializer(types, many=True).data
        return Response(types)


class RestaurantTypeViewSet(ModelViewSet):
    serializer_class = RestaurantTypeSerializer
    permission_classes = [my_perms.IsAdminOrReadOnly]
    queryset = RestaurantType.objects.all()


class RestaurantViewSet(ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Restaurant.objects.all()

    def _get_recommended_restaurants(self) -> queryset:
        queryset = self.get_queryset()
        recommended = queryset.all().annotate(rates_avg=Avg('rates__stars'))
        return recommended

    def _get_special_restaurants(self) -> queryset:
        queryset = self.get_queryset()
        special_offers_restaurants = queryset.filter(Q(menus__discount__gt=0) | Q(on_special_day=True))
        return special_offers_restaurants

    @action(['get'], detail=False, url_path="get-home")
    def home(self, request, *args, **kwargs):
        recommended = self._get_recommended_restaurants().order_by('?')[:5]
        special = self._get_special_restaurants().order_by('?')[:5]
        all_restaurants = self.get_queryset().order_by('?')[:5]
        recommended = self.get_serializer(recommended, many=True).data
        special = self.get_serializer(special, many=True).data
        all_restaurants = self.get_serializer(all_restaurants, many=True).data
        response = {
            'recommended': recommended,
            'special': special,
            'all': all_restaurants
        }
        return Response(response)

    @action(['get'], detail=False, url_path="special-offers")
    def special_offers(self, request, *args, **kwargs):
        serializer = self.get_serializer(self._get_special_restaurants().order_by('-created_at'), many=True)
        return Response(serializer.data)

    @action(['get'], detail=False, url_path="recommended-offers")
    def recommended_offers(self, request, *args, **kwargs):
        serializer = self.get_serializer(self._get_recommended_restaurants().order_by('-rates_avg'), many=True)
        return Response(serializer.data)

    @action(['get'], detail=True, url_path="restaurant-menus")
    def get_restaurant_menus(self, request, *args, **kwargs):
        categorized_menus = Menu.objects.grouped_by_meal_type_for_a_restaurant(restaurant_id=self.kwargs.get('pk'))
        return Response(categorized_menus)


class MenuViewSet(ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Menu.objects.all()

    @action(['get'], detail=False, url_path="get-home")
    def home(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        special_offers = queryset.filter(~Q(discount=0)).order_by('?')[:5]
        recommended = queryset.all().order_by('?')[:5]
        special_offers = self.get_serializer(special_offers, many=True).data
        recommended = self.get_serializer(recommended, many=True).data
        response = {
            'recommended': recommended,
            'special_offers': special_offers
        }
        return Response(data=response)

    @action(['get'], detail=False, url_path="special-offers")
    def special_offers(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        special_offers = queryset.filter(~Q(discount=0)).order_by('-created_at')
        serializer = self.get_serializer(special_offers, many=True)
        return Response(serializer.data)

    @action(['get'], detail=False, url_path="recommended-offers")
    def recommended_offers(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        recommended = queryset.all().order_by('-created_at')
        serializer = self.get_serializer(recommended, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderWRestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all().order_by('-created_at')

    def get_serializer(self, *args, **kwargs):
        if self.action == "create":
            return OrderSerializer(*args, **kwargs)
        return super(OrderViewSet, self).get_serializer(*args, **kwargs)

    def get_queryset(self):
        return super(OrderViewSet, self).get_queryset().filter(client=self.request.user.client)

    def create(self, request, *args, **kwargs):
        fixer = RequestDataFixer(request=request)
        return super(OrderViewSet, self).create(fixer, *args, **kwargs)


class OrderLineViewSet(ModelViewSet):
    serializer_class = OrderLineSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = OrderLine.objects.all()


class WilayaViewSet(ModelViewSet):
    serializer_class = WilayaSerializer
    permission_classes = [my_perms.IsAdminOrReadOnly]
    queryset = Wilaya.objects.all()


class CityViewSet(ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = [my_perms.IsAdminOrReadOnly]
    queryset = City.objects.all()


def version(request):
    print('inside this')
    if request.GET.get('code', None):
        code = request.GET.get('code')
        AppVersion.objects.all().update(code=code)
        return JsonResponse({'updated': True})
    else:
        code = AppVersion.objects.all().first().code
        return JsonResponse({'code': code})


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Address.objects.all()

    @action(['PUT'], detail=True, url_path="set-default", url_name='set-default')
    def set_default(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.default = True
        instance.save()
        self.get_queryset().filter(~Q(pk=instance.pk), belongs_to=request.user.client).update(default=False)
        return Response(self.get_serializer(instance).data)

    @action(['PUT'], detail=False, url_path="set-main", url_name='set-main')
    def set_main(self, request, *args, **kwargs):
        self.get_queryset().filter(belongs_to=request.user.client).update(default=False)
        return Response({"status": True})

    def get_queryset(self):
        return super(AddressViewSet, self).get_queryset().filter(belongs_to=self.request.user.client)


class PhoneViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PhoneSerializer
    queryset = Phone.objects.all()

    @action(['PUT'], detail=False, url_path="set-main", url_name='set-main')
    def set_main(self, request, *args, **kwargs):
        self.get_queryset().filter(user=request.user).update(default=False)
        return Response({"status": True})

    @action(['PUT'], detail=True, url_path="set-default", url_name='set-default')
    def set_default(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.default = True
        instance.save()
        self.get_queryset().filter(~Q(pk=instance.pk), user=request.user).update(default=False)
        return Response(self.get_serializer(instance).data)

    def get_queryset(self):
        return self.get_queryset().filter(user=self.request.user)

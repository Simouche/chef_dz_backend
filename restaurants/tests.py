from django.forms import formset_factory
from django.test import TestCase, RequestFactory
from django.urls import reverse

from restaurants.forms import MenuForm, OrderLineForm
from restaurants.models import (City, Client, MealType, Menu, OfferType, Restaurant, User, Wilaya, Order, OrderLine)
from restaurants.views import MenuCreateView, RestaurantListView


class OrderLineTestCase(TestCase):

    def setUp(self) -> None:
        # create the test user to make orders
        user = User.objects.create(username="Tester", first_name="tester_name", last_name="tester_name",
                                   phone="+213899136333", user_type="C")
        user.set_password("123456789")
        user.save()
        Client.objects.create(owner=user)

        # create the restaurant owner  and his restaurant for the menus
        owner = User.objects.create(username="TesterRestaurantOwner", first_name="tester_name", last_name="tester_name",
                                    phone="+213899136334", user_type="O")
        owner.set_password("123456789")
        City.objects.create(wilaya=Wilaya.objects.create(name="test", matricule=1, code_postal=10), name="test",
                            code_postal=19)
        restaurant = Restaurant.objects.create(name="test", registre_commerce="12345678913", id_fiscale="123456789",
                                               latitude=15.03, longitude=5.02, main_user=owner,
                                               address="dfqsdfqsdfqsdf", city_id=1)
        OfferType.objects.create(type="test")
        MealType.objects.create(type="test")
        Menu.objects.create(number=1, name="test", description="test", price=100.0, offered_by=restaurant, type_id=1,
                            offer_id=1, discount=0)
        Menu.objects.create(number=2, name="test2", description="test2", price=100.0, offered_by=restaurant, type_id=1,
                            offer_id=1, discount=0)

    def test_create_order_line_creation(self):
        test_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-MIN_NUM_FORMS': '',
            'form-0-number': 1,
            'form-0-menu': 1,
            'form-0-quantity': 10,
            'form-1-number': 2,
            'form-1-menu': 2,
            'form-1-quantity': 5
        }
        order = Order.objects.create(number=1, client_id=1)
        form_set = formset_factory(OrderLineForm, extra=2, min_num=1, validate_min=True)
        forms = form_set(test_data)
        self.assertTrue(forms.is_valid(), forms.errors)
        for form in forms:
            line = form.save()
            line.order = order
            line.save()
        self.assertEqual(OrderLine.objects.all().count(), 2)
        self.assertNotEqual(OrderLine.objects.all().count(), 3)
        order.delete()
        self.assertNotEqual(OrderLine.objects.all().count(), 2)
        self.assertEqual(OrderLine.objects.all().count(), 0)


class MenuFormTest(TestCase):

    def setUp(self) -> None:
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        # create the dependencies for the menus
        OfferType.objects.create(type="test")
        MealType.objects.create(type="test")
        city = City.objects.create(wilaya=Wilaya.objects.create(name="test", matricule=1, code_postal=10), name="test",
                                   code_postal=19)

        # create user 1 and his restaurant
        self.owner_success = User.objects.create(username="TesterRestaurantOwner", first_name="tester_name",
                                                 last_name="tester_name",
                                                 phone="+213899136334", user_type="O")
        self.owner_success.set_password("123456789")
        Restaurant.objects.create(name="test", registre_commerce="123456789131", id_fiscale="1234567819",
                                  latitude=15.03, longitude=5.02, main_user=self.owner_success,
                                  address="dfqsdfqsdfqsdf", city=city, images="sdfqsdf")

        # create user 2 and his restaurant
        self.owner_fail = User.objects.create(username="TesterRestaurantOwner2", first_name="tester_name",
                                              last_name="tester_name",
                                              phone="+213899136335", user_type="O")
        self.owner_fail.set_password("123456789")
        Restaurant.objects.create(name="test", registre_commerce="12345678913", id_fiscale="123456789",
                                  latitude=15.03, longitude=5.02, main_user=self.owner_fail,
                                  address="dfqsdfqsdfqsdf", city=city, images="dqsfqsdfqfg")

    def test_menu_creation_form(self):
        data_success = dict(
            number=1,
            name="test",
            description="test",
            price=1500.5,
            offered_by=self.owner_success.pk,
            type=2,
            offer=2
        )
        data_fail = dict(
            number=1,
            name="test",
            description="test",
            price=1500.5,
            offered_by=2,
            type=1,
            offer=1
        )
        request_success = self.factory.post("/restaurant/menu/create/", data_success)
        request_success.user = self.owner_success
        view = MenuCreateView()
        view.setup(request_success)
        self.assertEqual(Menu.objects.all().count(), 1, view.get_context_data()['form'].errors)

    def test_menu_creation_context(self):
        response = self.client.get(reverse('restaurants:create-menu'))
        self.assertTrue(isinstance(response.context['form'], MenuForm))


class RestaurantTestCase(TestCase):
    def setUp(self) -> None:
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_restaurants_list(self):
        request = self.factory.get("restaurant/restaurants/all/")
        view = RestaurantListView()
        view.setup(request)
        restaurants = view.get_context_data()['restaurant']
        for restaurant in restaurants:
            if restaurant.logo:
                self.assertTrue(isinstance(restaurant.logo.url, str))

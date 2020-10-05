from django.db.models import Manager, F


class CustomMenusManager(Manager):

    def grouped_by_meal_type(self):
        from restaurants.models import MealType
        menus = {}
        types = MealType.objects.all().values_list('type', flat=True)
        for typ in types:
            menus[typ] = []
        all_menus = self.all()
        for menu in all_menus:
            menus[menu.type.type].append(menu)
        return menus

    def grouped_by_meal_type_for_a_restaurant(self, restaurant_id):
        from restaurants.models import MealType, Restaurant
        menus = []
        types = MealType.objects.all().values_list('type', flat=True)
        for typ in types:
            menus.append({'name': typ, 'items': []})
        all_menus = self.filter(offered_by_id=restaurant_id).values('id', 'number', 'name', 'description', 'price',
                                                                    'image', 'offered_by_id', 'type_id',
                                                                    'offer_id', 'cuisine_id', 'discount',
                                                                    type_name=F('type__type'))
        for menu in all_menus:
            for typ in menus:
                if typ['name'] == menu['type_name']:
                    typ['items'].append(menu)
        return menus

    def grouped_by_offer_type(self):
        from restaurants.models import OfferType
        menus = {}
        offers = OfferType.objects.all().values_list('type', flat=True)
        for offer in offers:
            menus[offer] = []
        all_menus = self.all()
        for menu in all_menus:
            menus[menu.offer.type].append(menu)
        return menus

import os



from django.contrib.auth.models import Group
from django.db.models import Avg, Count, QuerySet
from django.forms import inlineformset_factory

from base_backend.utils import handle_uploaded_file
from delivery.models import DeliveryGuy, VehicleType
from recipe.models import Recipe
from restaurants.models import User, City, Restaurant, Cuisine, RestaurantType, RestaurantMealTypes, Client, Address, \
    WorksAt, Wilaya, Menu, MealType, OfferType, Order, OrderLine
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Username")
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )


class OtpForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Code')
            }
        )
    )


class BaseRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Username")
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("First Name")
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Last Name")
            }
        )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Phone Number")
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )
    c_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'placeholder': _('Birth Date')
            }
        )
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': _("Email")
            }
        )
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': _('Address')
            }
        )
    )
    lives_in = forms.ModelChoiceField(
        required=False,
        queryset=City.objects.all()
    )

    works_at = forms.ModelChoiceField(
        queryset=Restaurant.objects.filter(visible=True),
        required=False,
        empty_label=_('Select a Restaurant')
    )
    vehicle_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.all(),
        required=False,

    )

    class Meta:
        model = User
        fields = ['username', 'phone', 'address', 'first_name', 'last_name', 'user_type', 'birth_date', 'gender',
                  'email', 'lives_in', 'works_at']

    def clean(self):
        super(BaseRegistrationForm, self).clean()
        if not self.cleaned_data.get('password') == self.cleaned_data.get('c_password'):
            raise forms.ValidationError(_("mots de passe qui ne correspondent pas!"))
        if self.cleaned_data.get('user_type ') == 'D' and not self.cleaned_data.get('vehicle_type', None):
            raise forms.ValidationError('Delivery Man should select a vehicle type')

    def save(self, commit=True):
        user = super(BaseRegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        user_type = self.cleaned_data['user_type']

        if user_type == 'C':
            user.groups.add(Group.objects.get(name='client'))
            user = Client.objects.create(owner=user)
        elif user_type == 'D':
            user.groups.add(Group.objects.get(name='delivery'))
            user = DeliveryGuy.objects.create(owner=user, vehicle=self.cleaned_data.get('vehicle_type'))
        elif user_type == 'A':
            user.groups.add(Group.objects.get(name='admin'))
        elif user_type == 'S':
            user.groups.add(Group.objects.get(name='staff'))
            if self.cleaned_data.get('works_at', None):
                user.worksat_set \
                    .add(WorksAt.objects.create(user=user, restaurant=self.cleaned_data.get('works_at', None)))
        elif user_type == 'O':
            user.groups.add(Group.objects.get(name='owner'))

        return user


class RegisterRestaurantForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Restaurant Name")
            }
        )
    )
    registre_commerce = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Registre Commerce")
            }
        )
    )
    id_fiscale = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Identifiant Fiscale")
            }
        )
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Address")
            }
        )
    )
    latitude = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Latitude')
            }
        )
    )
    longitude = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Longitude')
            }
        )
    )
    logo = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'placeholder': _('Logo')
            }
        )
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Phone")
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': _('Email')
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Description")
            }
        )
    )
    open_at = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': _('Opens At')
            }
        )
    )
    close_at = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': _('Closes At')
            }
        )
    )

    cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all())
    types = forms.ModelMultipleChoiceField(queryset=RestaurantType.objects.all())
    meal_types = forms.ModelMultipleChoiceField(queryset=MealType.objects.all())
    city = forms.ModelChoiceField(queryset=City.objects.all())
    main_user = forms.ModelChoiceField(
        queryset=User.objects.filter(user_type='O'),
        required=False
    )  # this field should be hidden

    def __init__(self, user_instance=None, *args, **kwargs):
        super(RegisterRestaurantForm, self).__init__(*args, **kwargs)
        if user_instance:
            self.fields["main_user"].initial = user_instance
            self.fields['main_user'].widget.attrs['readonly'] = True
            self.fields['main_user'].disabled = True

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['main_user'].widget.attrs['readonly'] = True
            self.fields['main_user'].disabled = True

    class Meta:
        model = Restaurant
        fields = ['name', 'registre_commerce', 'id_fiscale', 'latitude', 'longitude', 'city', 'main_user', 'address',
                  'logo', 'phone', 'email', 'description', 'open_at', 'close_at',
                  'cuisines', 'types', 'meal_types']

    def save(self, commit=True):
        restaurant = super(RegisterRestaurantForm, self).save(commit=True)
        if self.files.getlist('images', None):
            for image in self.files.getlist('images', None):
                handle_uploaded_file(image, os.path.join(restaurant.images, image.name))
        return restaurant


class RestaurantSearchForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Restaurant Name")
            }
        ),
        required=False
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Address")
            }
        ),
        required=False
    )
    latitude = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Latitude')
            }
        ),
        required=False
    )
    longitude = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Longitude')
            }
        ),
        required=False
    )
    open_at = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': _('Opens At')
            }
        ),
        required=False
    )
    close_at = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': _('Closes At')
            }
        ),
        required=False
    )

    cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all())
    types = forms.ModelMultipleChoiceField(queryset=RestaurantType.objects.all())
    meal_types = forms.ModelMultipleChoiceField(queryset=MealType.objects.all())
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)

    class Meta:
        model = Restaurant
        fields = ['name', 'latitude', 'longitude', 'city', 'address', 'open_at', 'close_at',
                  'cuisines', 'types', 'meal_types']

    def search(self) -> QuerySet:
        queryset = Restaurant.objects.all()
        data = self.cleaned_data
        if data.get('name', None):
            queryset = queryset.filter(name__icontains=self.cleaned_data.get('name', None))
        if data.get('latitude', None):
            queryset = queryset.filter(latitude__lte=(data.get('latitude', None) - 5),
                                       latitude__gte=(data.get('latitude', None) - 5))
        if data.get('latitude', None):
            queryset = queryset.filter(longitude__lte=(data.get('longitude', None) - 5),
                                       longitude__gte=(data.get('longitude', None) - 5))
        if data.get('city', None):
            queryset = queryset.filter(city=data.get('city', None))
        if data.get('address', None):
            queryset = queryset.filter(address__icontains=data.get('address', None))
        if data.get('open_at', None):
            queryset = queryset.filter(open_at__gte=data.get('open_at', None))
        if data.get('close_at', None):
            queryset = queryset.filter(close_at__gte=data.get('close_at', None))
        if data.get('cuisines', None):
            queryset = queryset.filter(cuisines__in=data.get('cuisines', None))
        if data.get('types', None):
            queryset = queryset.filter(types__in=data.get('types', None))
        if data.get('meal_types', None):
            queryset = queryset.filter(meal_types__in=data.get('meal_types', None))

        return queryset

    def save(self, commit=True):
        pass


class AddUserAddress(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Address")
            }
        )
    )
    belongs_to = forms.ModelChoiceField(queryset=Client.objects.all())

    class Meta:
        model = Address
        fields = ['address', 'belongs_to']


class WorkAtForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type='S').order_by('pk'))
    restaurant = forms.ModelChoiceField(queryset=Restaurant.objects.all(), empty_label=_('Select a restaurant'))

    class Meta:
        model = WorksAt
        fields = ['user', 'restaurant']

    def __init__(self, user_instance=None, *args, **kwargs):
        super(WorkAtForm, self).__init__(*args, **kwargs)
        if user_instance:
            self.user = user_instance


class FilterRecipeForm(forms.Form):
    wilaya = forms.ModelChoiceField(queryset=Wilaya.objects.all(), required=False)
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all(), required=False)
    popularity = forms.BooleanField(required=False)
    rating = forms.BooleanField(required=False)
    recently_added = forms.BooleanField(required=False)

    def filter(self):
        queryset = Recipe.objects.all().annotate(avg=Avg('stars')).annotate(likes_=Count('likes'))
        data = self.cleaned_data
        if data.get('wilaya', None):
            queryset = queryset.filter(published_by__profile__owner__lives_in__wilaya=data['wilaya'])
        if data.get('cuisine', None):
            queryset = queryset.filter(cuisine=data['cuisine'])
        if data.get('popularity', False):
            queryset = queryset.order_by('-likes_')
        elif data.get('rating', False):
            queryset = queryset.order_by('-avg')
        elif data.get('recently_added'):
            queryset = queryset.order_by('-created_at')
        return queryset


class   MenuForm(forms.ModelForm):
    number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Number')
            }
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Menu Name")
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _("Description")
            }
        )
    )
    price = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Price')
            }
        )
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'placeholder': _('Menu Image')
            }
        ), required=False
    )
    offered_by = forms.ModelChoiceField(
        queryset=Restaurant.objects.all(), required=False,
        widget=forms.Select(
            attrs={
                'visibility': 'hidden'
            }
        ),
    )
    type = forms.ModelChoiceField(queryset=MealType.objects.all())
    offer = forms.ModelChoiceField(queryset=OfferType.objects.all())
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all())

    def __init__(self, queryset=None, *args, **kwargs):
        super(MenuForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['offered_by'].queryset = queryset

    class Meta:
        model = Menu
        fields = ['number', 'name', 'description', 'price', 'image', 'offered_by', 'type', 'offer', 'discount',
                  'cuisine']


class MenuSearchForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Menu Name")
            }
        )
    )
    price = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Price')
            }
        )
    )
    discount = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                'placeholder': _('Discount')
            }
        )
    )

    type = forms.ModelChoiceField(queryset=MealType.objects.all(), required=False)
    offer = forms.ModelChoiceField(queryset=OfferType.objects.all(), required=False)
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all(), required=False)

    class Meta:
        model = Menu
        fields = ['name', 'price', 'type', 'offer', 'discount', 'cuisine']

    def save(self, commit=True):
        pass

    def search(self, owner):
        queryset = Menu.objects.filter(offered_by_id=owner)
        data = self.cleaned_data

        if data.get('name', None):
            queryset = queryset.filter(name__icontains=data.get('name', None))
        if data.get('price', None):
            queryset = queryset.filter(price__lte=data.get('price', None))
        if data.get('type', None):
            queryset = queryset.filter(type=data.get('type', None))
        if data.get('offer', None):
            queryset = queryset.filter(offer=data.get('offer', None))
        if data.get('discount', False):
            queryset = queryset.filter(discount__gt=0)
        if data.get('cuisine', None):
            queryset = queryset.filter(cuisine=data.get('cuisine', None))

        return queryset


class OrderForm(forms.ModelForm):
    number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Number')
            }
        )
    )
    client = forms.ModelChoiceField(queryset=Client.objects.all())

    class Meta:
        model = Order
        fields = ['number', 'client']


class OrderLineForm(forms.ModelForm):
    number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Number')
            }
        )
    )
    menu = forms.ModelChoiceField(queryset=Menu.objects.all())
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': _('Quantity')
            }
        )
    )
    order = forms.ModelChoiceField(queryset=Order.objects.all(), required=False)

    class Meta:
        model = OrderLine
        fields = ['number', 'menu', 'quantity', 'order']

    def save(self, commit=True):
        return super(OrderLineForm, self).save(commit=False)


OrderLines = inlineformset_factory(parent_model=Order, model=OrderLine, fields=('number', 'menu', 'quantity'), extra=1,
                                   can_delete=True)

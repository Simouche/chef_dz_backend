from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, ListView, CreateView, DeleteView, DetailView, UpdateView

from base_backend.models import Round
from base_backend.utils import activate_user_over_otp
from recipe.models import Recipe, Participant
from restaurants.forms import LoginForm, BaseRegistrationForm, OtpForm, FilterRecipeForm, OrderLineForm, MenuForm, \
    RegisterRestaurantForm, RestaurantSearchForm, MenuSearchForm
from restaurants.models import Wilaya, Cuisine, RestaurantType, MealType, OfferType, Order, OrderLine, Restaurant, Menu, \
    User


class Home(View):
    template_name = 'restau/index.html'
    login_form = LoginForm()

    def get(self, request):
        user_avg = None
        if request.user.is_authenticated and 'client' in request.user.groups.all() and \
                request.user.client.is_participant:
            user_avg = Participant.objects.filter(pk=request.user.client.participant.pk) \
                .annotate(likes_=Count("recipes__likes")).annotate(avg=Round(Avg('recipes__stars__stars'), 1))[0]

        recipes = Recipe.objects.all().annotate(avg=Round(Avg('stars__stars'), 1)).annotate(likes_=Count('likes')) \
            .annotate(comments_=(Count('comments'))).order_by('-created_at')
        wilayas = Wilaya.objects.all()
        cuisines = Cuisine.objects.all()
        restaurants = Restaurant.objects.all().order_by('?')[0:11]
        context = {
            'login_form': self.login_form,
            'recipes': recipes,
            'wilayas': wilayas,
            'cuisines': cuisines,
            'user_avg': user_avg,
            'restaurants': restaurants
        }
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        filter_form = FilterRecipeForm(request.POST)
        if filter_form.is_valid():
            data_filtered = filter_form.filter()
            html = render_to_string(template_name="list_recipe.html",
                                    context={"data": data_filtered})
            return JsonResponse(data={'html': html})
        else:
            return JsonResponse(data={'html': "Empty"})


class coming_soon(View):
    template_name = 'coming_soon.html'

    def get(self, request):
        context = dict()
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = 'restau/login_page.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('restaurants:home')

        login_form = LoginForm()
        context = dict(login_form=login_form)
        return render(request, self.template_name, context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data.get('username'),
                                password=login_form.cleaned_data.get('password'))
            if user:
                login(request, user)
                if request.GET.get('next', None):
                    return redirect(request.GET.get('next'))
                return redirect('restaurants:home')
            else:
                login_form.add_error(None, _('Invalid username/password'))
                context = dict(login_form=login_form)
                return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('restaurants:home')


class RegistrationView(FormView):
    template_name = 'restau/register.html'
    success_url = 'restaurants:login'  # todo change this to otp or email verification
    login_form = LoginForm()
    form_class = BaseRegistrationForm

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['loginform'] = self.login_form
        return context

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class Dashboard(View):
    template_name = 'restau\index.html'

    def get(self, request):
        context = dict()
        return render(request, self.template_name, context)
        pass


class VerificationOTPView(View):
    template_name = 'OtpVerification.html'

    def get(self, request):
        form = OtpForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        form = OtpForm(request.POST)

        if form.is_valid():
            result = activate_user_over_otp(form.cleaned_data.get('code'))
            if result:
                return redirect('restaurants:login')
            form.add_error('', _('Code déja utilisé ou exipré!'))
            context = {
                'form': form
            }
            return render(request, self.template_name, context)


# restaurant type
class RestaurantTypesList(ListView):
    model = RestaurantType
    ordering = "type"
    queryset = RestaurantType.objects.all()
    template_name = ""
    context_object_name = "types"


class RestaurantTypeCreate(CreateView):
    model = RestaurantType
    fields = ['type']
    success_url = ""  # TODO: make it reverse to the types list


# restaurant cuisine
class RestaurantCuisinesList(ListView):
    model = Cuisine
    ordering = "name"
    queryset = Cuisine.objects.all()
    template_name = ""
    context_object_name = "cuisines"


class RestaurantCuisineCreate(CreateView):
    model = Cuisine
    fields = ['name']
    success_url = ""  # TODO: make it reverse to the cuisines list


# restaurant meal type
class RestaurantMealList(ListView):
    model = MealType
    ordering = "type"
    queryset = MealType.objects.all()
    template_name = ""
    context_object_name = "meals"


class RestaurantMealCreate(CreateView):
    model = MealType
    fields = ['type']
    success_url = ""  # TODO: make it reverse to the meal types list


# restaurant offer type
class RestaurantOfferList(ListView):
    model = OfferType
    ordering = "type"
    queryset = OfferType.objects.all()
    template_name = ""
    context_object_name = "offers"


class RestaurantOfferTypeCreate(CreateView):
    model = OfferType
    fields = ['type']
    success_url = ""  # TODO: make it reverse to the offer types list


# orders and order lines
class OrdersMixin:
    def my_get_queryset(self):
        groups = self.request.user.groups.all().values_list('name', flat=True)
        if "client" in groups:
            return self.queryset.filter(visible=True, client=self.request.user)
        elif "owner" in groups:
            return self.queryset.filter(visible=True,
                                        lines__menu__offered_by__in=self.request.user.restaurant_set.all()) \
                .distinct("id")
        elif "staff" in groups:
            return self.queryset.filter(visible=True, lines__menu__offered_by_id__in=self.request.user.worksat_set
                                        .filter(visible=True).values_list('id', flat=True)).distinct("id")
        else:
            return self.queryset


class OrderCreateView(FormView):
    template_name = "restau/order_confirmed.html"
    success_url = reverse_lazy("details-order")  # TODO: reverse to the user orders list
    form_class = formset_factory(OrderLineForm, extra=2, min_num=1, validate_min=True)

    def form_valid(self, forms):
        order = Order.objects.create(number=Order.generate_number(), client=self.request.user.client)
        for form in forms:
            line = form.save()
            line.order = order
            line.save()
            if not order.restaurant:
                order.restaurant = line.menu.offered_by
                order.save()
        return HttpResponseRedirect(self.get_success_url(), pk=order.pk)


class OrderUpdateView(UpdateView, OrdersMixin):
    model = Order
    fields = ['status', 'visible']
    template_name = "ok.html"
    success_url = ""  # TODO: reverse here


class OrderListView(ListView, OrdersMixin):
    template_name = "restau/list_orders.html"
    ordering = "-created_at"
    queryset = Order.objects.all()
    context_object_name = "orders"

    def get_queryset(self):
        self.my_get_queryset()
        return super(OrderListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        total = 0
        if kwargs.get('object_list'):
            for order in kwargs.get('object_list'):
                total += order.sub_total
        context['total'] = total
        return context


class OrderDeleteView(DeleteView, OrdersMixin):
    model = Order
    success_url = ""  # TODO: revese to the orders list, override the success url if needed

    def get_queryset(self):
        self.my_get_queryset()
        return super(OrderDeleteView, self).get_queryset()


class OrderDetailsView(DetailView, OrdersMixin):
    model = Order
    context_object_name = "order"
    queryset = Order.objects.filter(visible=True)
    template_name = ""

    def get_queryset(self):
        self.my_get_queryset()
        return super(OrderDetailsView, self).get_queryset()


class OrderLineDeleteView(DeleteView):
    model = OrderLine
    context_object_name = "orderline"
    queryset = OrderLine.objects.filter(order__visible=True)
    template_name = ""


class OrderLineUpdateView(UpdateView):
    model = OrderLine
    fields = ['menu', 'quantity']
    template_name = ""
    success_url = ""  # TODO: reverse here


# TODO: add a new order line

# Menu
class MenuViewsMixin:

    def my_form_kwargs(self):
        groups = self.request.user.groups.all().values_list('name', flat=True)
        if 'owner' in groups:
            self.kwargs['queryset'] = Restaurant.objects.filter(main_user=self.request.user)
        elif 'staff' in groups:
            self.kwargs['queryset'] = Restaurant.objects.filter(id__in=self.request.user.worksat_set
                                                                .filter(visible=True)
                                                                .values_list('restaurant_id', flat=True))
        else:
            self.kwargs['queryset'] = Restaurant.objects.all()

    def my_get_queryset(self):
        groups = self.request.user.groups.all().values_list('name', flat=True)
        if 'owner' in groups:
            if self.kwargs.get('pk', None):
                self.queryset = Menu.objects.filter(offered_by__main_user=self.request.user,
                                                    offered_by_id=self.kwargs.get('pk', None))
            else:
                self.queryset = Menu.objects.filter(offered_by__main_user=self.request.user)
        elif 'staff' in groups:
            if self.kwargs.get('pk', None):
                self.queryset = Menu.objects.filter(offered_by_id__in=self.request.user.worksat_set
                                                    .filter(visible=True)
                                                    .values_list('restaurant_id', flat=True),
                                                    offered_by_id=self.kwargs.get('pk', None))
            else:
                self.queryset = Menu.objects.filter(offered_by_id__in=self.request.user.worksat_set
                                                    .filter(visible=True)
                                                    .values_list('restaurant_id', flat=True))
        else:
            if self.kwargs.get('pk', None):
                self.queryset = Menu.objects.filter(offered_by_id=self.kwargs.get('pk', None))
            else:
                self.queryset = Menu.objects.all()


# TODO: implement the get success url

class Meta:
    abstract = True


class MenuCreateView(FormView, MenuViewsMixin):
    form_class = formset_factory(MenuForm, extra=0, min_num=1, validate_min=True)
    success_url = ""  # TODO: reverse here
    template_name = "restau/add_menu.html"

    def get_form_kwargs(self):
        self.my_form_kwargs()
        return super(MenuCreateView, self).get_form_kwargs()

    def form_valid(self, forms):
        for form in forms:
            form.cleaned_data['offered_by'] = self.request.GET.get('restaurant')
            form.save()
        return self.get_success_url()


class MenuUpdateView(UpdateView, MenuViewsMixin):
    form_class = MenuForm
    queryset = Menu.objects.all()
    success_url = ""  # TODO: reverse this
    template_name = "ok.html"

    def get_queryset(self):
        self.my_get_queryset()
        return super(MenuUpdateView, self).get_queryset()

    def get_form_kwargs(self):
        self.my_form_kwargs()
        return super(MenuUpdateView, self).get_form_kwargs()


class MenuDeleteView(DeleteView, MenuViewsMixin):
    model = Menu
    template_name = ""
    success_url = ""  # TODO: reverse this
    queryset = Menu.objects.all()

    def get_queryset(self):
        self.my_get_queryset()
        return super(MenuDeleteView, self).get_queryset()


class MenuListView(ListView, MenuViewsMixin):
    model = Menu
    template_name = "restau/menu.html"
    queryset = Menu.objects.all()
    ordering = "-created_at"
    paginate_by = 25
    context_object_name = "menu_list"

    def get_queryset(self):
        self.my_get_queryset()
        return super(MenuListView, self).get_queryset()


class MenuSearchListView(ListView):
    model = Menu
    template_name = "restau/menu_order.html"
    queryset = Menu.objects.all()
    context_object_name = "menu_list"
    form = None
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MenuSearchListView, self).get_context_data(object_list=object_list, **kwargs)
        context["search_form"] = self.form or RestaurantSearchForm()
        context["order_form"] = formset_factory(OrderLineForm, extra=2, min_num=1, validate_min=True)
        context["restaurant"] = get_object_or_404(Restaurant, pk=self.kwargs.get('pk', 0))
        return super(MenuSearchListView, self).get_context_data(**context)

    def get_queryset(self):
        if self.request.method == 'POST':
            search_form = MenuSearchForm(self.request.POST)
            if search_form.is_valid():
                return search_form.search(self.kwargs.get('pk', 0))
            self.form = search_form
        return Menu.objects.filter(offered_by_id=self.kwargs.get('pk', None))


class MenuDetailsView(DetailView, MenuViewsMixin):
    model = Menu
    template_name = ""
    context_object_name = "menu"
    queryset = Menu.objects.all()

    def get_queryset(self):
        self.my_get_queryset()
        return super(MenuDetailsView, self).get_queryset()


# Restaurant
class RestaurantMixin:

    def my_get_queryset(self):
        groups = self.request.user.groups.all().values_list('name', flat=True)
        if 'owner' in groups:
            self.queryset = Restaurant.objects.filter(main_user=self.request.user)
        elif 'staff' in groups:
            self.queryset = Restaurant.objects.filter(id__in=self.request.user.worksat_set
                                                      .filter(visible=True)
                                                      .values_list('restaurant_id', flat=True))
        else:
            self.queryset = Restaurant.objects.all()


class RestaurantCreateView(CreateView):
    form_class = RegisterRestaurantForm
    success_url = 'restaurants:list-restaurant'  # TODO: reverse here
    template_name = "restau/add_restau.html"
    model = Restaurant

    def get_form_kwargs(self):
        kwargs = super(RestaurantCreateView, self).get_form_kwargs()
        groups = self.request.user.groups.all().values_list('name', flat=True)
        if 'owner' in groups:
            kwargs['user_instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return self.get_success_url()

    def form_invalid(self, form):
        print(form.errors)
        return super(RestaurantCreateView, self).form_invalid(form)


class RestaurantUpdateView(UpdateView, RestaurantMixin):
    form_class = RegisterRestaurantForm
    success_url = ""  # TODO: reverse here
    template_name = ""
    model = Restaurant
    queryset = Restaurant.objects.all()

    def get_queryset(self):
        self.my_get_queryset()
        return super(RestaurantUpdateView, self).get_queryset()


class RestaurantDeleteView(DeleteView, RestaurantMixin):
    model = Restaurant
    template_name = ""
    success_url = ""  # TODO: reverse here
    queryset = Restaurant.objects.all()

    def get_queryset(self):
        self.my_get_queryset()
        return super(RestaurantDeleteView, self).get_queryset()


class RestaurantDetailsView(DetailView, RestaurantMixin):
    model = Restaurant
    template_name = "restau/detail_restau.html"
    queryset = Restaurant.objects.all()
    context_object_name = "restaurant"

    def get_queryset(self):
        self.my_get_queryset()
        return super(RestaurantDetailsView, self).get_queryset()


class RestaurantsSearchList(ListView):
    model = Restaurant
    template_name = "restau/list_restau.html"
    queryset = Restaurant.objects.all()
    context_object_name = "restaurants"
    form = None
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RestaurantsSearchList, self).get_context_data(object_list=object_list, **kwargs)
        context["search_form"] = self.form or RestaurantSearchForm()
        return super(RestaurantsSearchList, self).get_context_data(**context)

    def get_queryset(self):
        if self.request.method == 'POST':
            search_form = RestaurantSearchForm(self.request.POST)
            if search_form.is_valid():
                return search_form.search()
            self.form = search_form
            return super(RestaurantsSearchList, self).get_queryset()

        return super(RestaurantsSearchList, self).get_queryset()


class RestaurantListView(ListView, RestaurantMixin):
    model = Restaurant
    template_name = "restau/list_page.html"
    queryset = Restaurant.objects.all()
    context_object_name = "restaurant"

    def get_queryset(self):
        self.my_get_queryset()
        return super(RestaurantListView, self).get_queryset()


# Client
class UserUpdateView(UpdateView):
    model = User
    success_url = ""  # TODO: make a reverse here
    template_name = ""

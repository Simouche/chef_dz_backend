"""
creates permission groups
to be used right after migrations
"""
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Create groups and initialize default permissions'

    GROUPS = ['client', 'participant', 'owner', 'staff', 'admin', 'delivery']
    RECIPE_APP_MODELS = list(apps.get_app_config("recipe").models)
    RESTAURANTS_APP_MODELS = list(apps.get_app_config("restaurants").models)
    MANAGEMENT_APP_MODELS = list(apps.get_app_config("management").models)
    DELIVERY_APP_MODELS = list(apps.get_app_config("delivery").models)

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force', type=bool,
                            help='forces the re-attribution of perms to the groups, should be used'
                                 ' in case of adding new models')

    def handle(self, *args, **options):
        force = options.get('force', False)
        self._init_delivery(force=force)
        self._init_participant(force=force)
        self._init_owner(force=force)
        self._init_clients(force=force)
        self._init_skylight(force=force)
        self._init_staff()
        print('created default groups and permissions.')

    def _init_delivery(self, force=False):
        delivery_perms = self.RECIPE_APP_MODELS
        self._init_group_('delivery', delivery_perms, force=force)

    def _init_participant(self, force=False):
        participant_perms = [perm for perm in self.RECIPE_APP_MODELS if
                             perm in ('recipe', 'contains', 'step')]
        all_models = participant_perms
        self._init_group_('participant', all_models, force=force)

    def _init_clients(self, force=False):
        client_perms = [perm for perm in self.RESTAURANTS_APP_MODELS if
                        perm in ('client', 'restaurant', 'orderline', 'order',
                                 'address')]  # TODO: there are more perms to add restaurant like...
        client_recipe_perms = [perm for perm in self.RECIPE_APP_MODELS if perm in (
            'starsrate', 'like', 'comment')]
        all_models = client_perms + client_recipe_perms
        self._init_group_('client', all_models, force=force)

    def _init_staff(self, force=False):
        staff_perms = [perm for perm in self.RESTAURANTS_APP_MODELS if
                       perm not in ('payment', 'address', 'passwordreset', 'smsverification', 'restaurantcuisines',
                                    'restautanttypes', 'restaurantmealtypes', 'worksat', 'user')]
        all_models = staff_perms
        self._init_group_('staff', all_models, force=force)

    def _init_owner(self, force=False):
        owner_perms = [perm for perm in self.RESTAURANTS_APP_MODELS if
                       perm not in ('address', 'passwordreset', 'smsverification')]
        self._init_group_('owner', owner_perms, force=force)

    def _init_skylight(self, force=False):
        all_models = self.RECIPE_APP_MODELS + self.RESTAURANTS_APP_MODELS + self.MANAGEMENT_APP_MODELS + \
                     self.DELIVERY_APP_MODELS
        self._init_group_('admin', all_models, force=force)

    def _init_group_(self, group_name: str, perms: list, perm_type=None, force=False) -> None:
        new_group, created = Group.objects.get_or_create(name=group_name)
        if not created and not force:
            print('group {} already created, if you want to force '
                  'the re-attribution of permissions please add  "--force=True" to the command .'.format(group_name))
            return
        for perm in perms:
            try:
                content_type = ContentType.objects.get(model=perm)
                if perm_type is not None:
                    permissions = Permission.objects.filter(content_type=content_type, codename__startswith=perm_type)
                else:
                    permissions = Permission.objects.filter(content_type=content_type)
                new_group.permissions.add(*permissions)
                print('{} group: adding all permissions on {}'.format(group_name, perm))
            except ContentType.DoesNotExist:
                pass

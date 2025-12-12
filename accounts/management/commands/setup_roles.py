from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from staff_management import models as sm

class Command(BaseCommand):
    help = 'Create Manager and Supervisor groups with sensible permissions.'

    def handle(self, *args, **opts):
        manager, _ = Group.objects.get_or_create(name='Manager')
        supervisor, _ = Group.objects.get_or_create(name='Supervisor')

        staff_ct = ContentType.objects.get_for_model(sm.Staff)
        wg_ct = ContentType.objects.get_for_model(sm.WeekendGroup)

        perms = list(Permission.objects.filter(content_type__in=[staff_ct, wg_ct]))
        supervisor.permissions.set(perms)
        manager.permissions.set(perms)

        self.stdout.write(self.style.SUCCESS('Roles created/updated'))
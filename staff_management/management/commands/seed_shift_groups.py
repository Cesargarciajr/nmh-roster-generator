from django.core.management.base import BaseCommand
from staff_management.models import ShiftGroup

class Command(BaseCommand):
    help = "Create default shift groups (Morning/Evening/Night) if missing."

    def handle(self, *args, **opts):
        defaults = [
            ("Morning", True, "Standard morning shift"),
            ("Evening", True, "Standard evening shift"),
            ("Night",   True, "Standard night shift"),
        ]
        created = 0
        for name, active, desc in defaults:
            _, was_created = ShiftGroup.objects.get_or_create(
                shift_name=name,
                defaults={"is_active": active, "description": desc},
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} shift groups (created if missing)."))
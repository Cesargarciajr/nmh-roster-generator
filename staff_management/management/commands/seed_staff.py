from __future__ import annotations

import random
from django.core.management.base import BaseCommand
from django.utils import timezone

from staff_management.models import Staff, ShiftGroup, WeekendGroup


FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Casey", "Riley", "Jamie", "Morgan",
    "Cameron", "Drew", "Blake", "Avery", "Hayden", "Quinn", "Rowan", "Elliot",
    "Parker", "Payton", "Dakota", "Reese", "Skyler", "Adrian", "Emerson", "Finley",
    "Kai", "Remy", "Toby",
]

LAST_NAMES = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davis",
    "Miller", "Moore", "Clark", "Wright", "Robinson", "Walker", "Hall", "Allen",
]


def random_name(i: int) -> tuple[str, str]:
    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    return fn, f"{ln}-{i:03d}"


class Command(BaseCommand):
    help = "Seed the database with sample staff for testing (creates ShiftGroups/WeekendGroups if needed)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=55, help="Number of staff to create")
        parser.add_argument("--force", action="store_true", help="Create even if staff exist")

    def handle(self, *args, **options):
        count = options["count"]
        force = options["force"]

        # Ensure some ShiftGroups exist
        sg_defs = [
            ("Night", 7, 4),
            ("Afternoon", 7, 4),
            ("Morning-Short", 1, 0),
            ("Morning-Full", 12, 11),
            ("Morning-Mid", 3, 3),
        ]
        created_sgs = []
        for name, wday_req, wend_req in sg_defs:
            sg, _ = ShiftGroup.objects.get_or_create(shift_name=name, defaults={
                "required_weekday": wday_req,
                "required_weekend": wend_req,
                "is_active": True,
            })
            created_sgs.append(sg)

        # Ensure weekend groups 1..4
        for i in range(1, 5):
            WeekendGroup.objects.get_or_create(number=i, defaults={"name": f"Week {i}"})

        existing = Staff.objects.count()
        if existing and not force:
            self.stdout.write(self.style.WARNING(f"{existing} staff already exist. Use --force to add anyway."))
            return

        start = timezone.now()
        created = 0
        for i in range(existing + 1, existing + 1 + count):
            fn, ln = random_name(i)
            employee_id = f"S{i:04d}"
            full_name = f"{fn} {ln}"
            gender = random.choice(["F", "M", "O"])
            staff = Staff.objects.create(full_name=full_name, employee_id=employee_id, gender=gender, active=True)

            # assign 1-3 random shift groups
            assign_count = random.choice([1, 1, 2, 3])
            groups = random.sample(created_sgs, k=assign_count)
            for g in groups:
                staff.shift_groups.add(g)

            # assign weekend group randomly
            wg = WeekendGroup.objects.order_by('?').first()
            staff.weekend_group = wg
            # short day randomly assigned to a weekday sometimes
            if random.random() < 0.2:
                staff.short_day_weekday = random.randint(0, 4)

            staff.save()
            created += 1

        elapsed = timezone.now() - start
        self.stdout.write(self.style.SUCCESS(f"Created {created} staff in {elapsed.total_seconds():.2f}s"))
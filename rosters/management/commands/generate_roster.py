from django.core.management.base import BaseCommand
from datetime import date, timedelta
from collections import defaultdict

from rosters.models import Roster, ShiftAssignment
from staff_management.models import Staff, ShiftGroup, WeekendGroup
from timeoff_requests.models import Holiday, Leave, DayOffRequest


class Command(BaseCommand):
    help = "Generate a roster following OFF-first logic with Mode-A fairness"

    def add_arguments(self, parser):
        parser.add_argument("--start", required=True)
        parser.add_argument("--days", type=int, default=7)
        parser.add_argument("--max-shifts", type=int, default=5)

    def handle(self, *args, **opts):
        start = date.fromisoformat(opts["start"])
        days = opts["days"]
        max_shifts = opts["max_shifts"]

        # Create roster
        roster = Roster.objects.create(
            start_date=start,
            end_date=start + timedelta(days=days - 1)
        )
        self.stdout.write(self.style.SUCCESS(f"Created roster {roster}"))

        # Build date list
        date_list = [start + timedelta(days=i) for i in range(days)]

        # Staff list
        staff_list = list(Staff.objects.filter(active=True))

        # Preload holidays / leaves / approved DORs
        holiday_map = defaultdict(set)
        leave_map = defaultdict(set)
        dors_map = defaultdict(set)

        for h in Holiday.objects.filter(start_date__lte=roster.end_date,
                                        end_date__gte=roster.start_date,
                                        status="APPROVED"):
            for d in date_list:
                if h.start_date <= d <= h.end_date:
                    holiday_map[h.staff_id].add(d)

        for lv in Leave.objects.filter(start_date__lte=roster.end_date,
                                       end_date__gte=roster.start_date,
                                       status="APPROVED"):
            for d in date_list:
                if lv.start_date <= d <= lv.end_date:
                    leave_map[lv.staff_id].add(d)

        for dor in DayOffRequest.objects.filter(date__in=date_list, status="APPROVED"):
            dors_map[dor.staff_id].add(dor.date)

        # WEEK SPLITTING (Mon–Sun blocks)
        weeks = [date_list[i:i + 7] for i in range(0, len(date_list), 7)]

        # Weekend group staff lookup
        wg_members = defaultdict(set)
        for wg in WeekendGroup.objects.all():
            members = Staff.objects.filter(weekend_group=wg).values_list("id", flat=True)
            wg_members[wg.number] = set(members)

        def find_consecutive_pair(days):
            """Return the first consecutive pair from a sorted list of dates."""
            days = sorted(days)
            for i in range(len(days) - 1):
                if (days[i + 1] - days[i]).days == 1:
                    return days[i], days[i + 1]
            return None

        # =====================================================================
        #                  FAIRNESS TRACKER (Mode A rotation)
        # =====================================================================
        fairness_rotation_index = defaultdict(int)

        # =====================================================================
        #                   STAGE 1 — CREATE OFF MAP
        # =====================================================================
        days_off_map = defaultdict(set)

        for staff in staff_list:
            sid = staff.id
            hol = holiday_map[sid]
            lev = leave_map[sid]
            approved = dors_map[sid]

            for wi, week in enumerate(weeks):

                # STEP 1: Approved DORs
                week_appr = sorted([d for d in approved if d in week])
                final_pair = None

                # A: Already 2 consecutive
                p = find_consecutive_pair(week_appr)
                if p:
                    final_pair = p

                # B: Only 1 approved → pair with neighbor
                if final_pair is None and len(week_appr) == 1:
                    ad = week_appr[0]
                    for c in [ad - timedelta(days=1), ad + timedelta(days=1)]:
                        if c in week and c not in hol and c not in lev:
                            final_pair = (min(ad, c), max(ad, c))
                            break

                # STEP 2: Weekend Group
                if final_pair is None:
                    wg_number = ((week[0].day - 1) // 7) + 1
                    if sid in wg_members.get(wg_number, []):
                        sat = next((d for d in week if d.weekday() == 5), None)
                        sun = next((d for d in week if d.weekday() == 6), None)
                        if sat and sun:
                            if (
                                sat not in hol and sat not in lev and
                                sun not in hol and sun not in lev
                            ):
                                final_pair = (sat, sun)

                # STEP 3: Mode A rotating fallback
                if final_pair is None:
                    rotation_pairs = [
                        (0, 1),  # Mon–Tue
                        (1, 2),  # Tue–Wed
                        (2, 3),  # Wed–Thu
                        (3, 4),  # Thu–Fri
                        (4, 5),  # Fri–Sat
                    ]

                    rot_index = fairness_rotation_index[sid]

                    for attempt in range(len(rotation_pairs)):
                        idx = (rot_index + attempt) % len(rotation_pairs)
                        p1, p2 = rotation_pairs[idx]

                        if p1 < len(week) and p2 < len(week):
                            d1, d2 = week[p1], week[p2]
                            if (
                                d1 not in hol and d2 not in hol and
                                d1 not in lev and d2 not in lev
                            ):
                                final_pair = (d1, d2)
                                fairness_rotation_index[sid] = (idx + 1) % len(rotation_pairs)
                                break

                # STEP 4 — Final fallback Mon/Tue
                if final_pair is None and len(week) >= 2:
                    final_pair = (week[0], week[1])

                # Record OFF days
                if final_pair:
                    days_off_map[sid].update(final_pair)

        self.stdout.write(self.style.SUCCESS("Computed OFF days."))

        # =====================================================================
        #                   STAGE 2 — ASSIGN SHIFTS WITH FAIRNESS
        # =====================================================================

        shift_groups = list(ShiftGroup.objects.filter(is_active=True))

        # Fatigue + fairness trackers
        last_night_worked = defaultdict(set)
        weekly_count = defaultdict(int)
        recent_pick = {}

        assignments_to_create = []

        for d in date_list:
            for sg in shift_groups:
                required = sg.required_weekday if d.weekday() < 5 else sg.required_weekend

                # ==== 1) Build eligibility list ====
                eligible = []
                for s in staff_list:
                    sid = s.id

                    if sg not in s.shift_groups.all():
                        continue

                    if (
                        d in days_off_map[sid]
                        or d in holiday_map[sid]
                        or d in leave_map[sid]
                    ):
                        continue

                    # Fatigue rule: no night → morning
                    if sg.shift_name.lower().startswith("morning"):
                        if (d - timedelta(days=1)) in last_night_worked[sid]:
                            continue

                    # Weekly max shifts
                    week_id = d.isocalendar()[1]
                    if weekly_count[(sid, week_id)] >= max_shifts:
                        continue

                    eligible.append(s)

                # ==== 2) Fairness: sort by fewest shifts in this week ====
                week_id = d.isocalendar()[1]
                eligible = sorted(
                    eligible,
                    key=lambda s: weekly_count[(s.id, week_id)]
                )

                assigned = 0

                for s in eligible:
                    sid = s.id

                    # Avoid repeating the same worker for same shift group
                    if recent_pick.get(sg.id) == sid and len(eligible) > 1:
                        continue

                    # Create assignment
                    assignments_to_create.append(
                        ShiftAssignment(
                            roster=roster,
                            shift_group=sg,
                            staff=s,
                            date=d
                        )
                    )

                    weekly_count[(sid, week_id)] += 1
                    recent_pick[sg.id] = sid

                    # Track night work
                    if sg.shift_name.lower().startswith("night"):
                        last_night_worked[sid].add(d)

                    assigned += 1
                    if assigned >= required:
                        break

        # Bulk save
        ShiftAssignment.objects.bulk_create(assignments_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(assignments_to_create)} shift assignments."
            )
        )

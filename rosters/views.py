from __future__ import annotations

from datetime import date
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages

from rosters.models import Roster
from rosters.models import ShiftAssignment
from staff_management.models import ShiftGroup
from timeoff_requests.models import Holiday, Leave, DayOffRequest
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from staff_management.models import Staff
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class GenerateRosterView(View):
    template_name = "rosters/generate.html"

    def get(self, request):
        # filters
        roster_id = request.GET.get("roster_id")
        weekend_group = request.GET.get("weekend_group")
        month = request.GET.get("month")  # YYYY-MM
        start_from = request.GET.get("start_from")
        start_to = request.GET.get("start_to")

        qs = Roster.objects.all().order_by("-start_date")
        if roster_id:
            qs = qs.filter(pk=roster_id)

        # apply date range filters
        if month:
            try:
                y, m = month.split("-")
                from calendar import monthrange
                y = int(y); m = int(m)
                first = date(y, m, 1)
                last = date(y, m, monthrange(y, m)[1])
                qs = qs.filter(start_date__gte=first, start_date__lte=last)
            except Exception:
                pass
        if start_from:
            try:
                qs = qs.filter(start_date__gte=date.fromisoformat(start_from))
            except Exception:
                pass
        if start_to:
            try:
                qs = qs.filter(start_date__lte=date.fromisoformat(start_to))
            except Exception:
                pass

        rosters = list(qs[:200])

        # compute weekend group mapping and build table rows
        from staff_management.models import WeekendGroup
        rows = []
        for r in rosters:
            # simple week-in-month heuristic
            week_number = ((r.start_date.day - 1) // 7) + 1
            wg = WeekendGroup.objects.filter(number=week_number).first()
            rows.append({
                "id": r.pk,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "assignments": r.assignments.count(),
                "weekend_group": wg.name if wg else f"Week {week_number}",
                "weekend_group_number": week_number,
                "object": r,
            })

        # provide weekend group choices for filter
        weekend_groups = list(WeekendGroup.objects.all())

        context = {
            "today": date.today(),
            "rosters": rosters,
            "rows": rows,
            "weekend_groups": weekend_groups,
            "filters": {
                "roster_id": roster_id or "",
                "weekend_group": weekend_group or "",
                "month": month or "",
                "start_from": start_from or "",
                "start_to": start_to or "",
            },
        }
        return render(request, self.template_name, context)

    def post(self, request):
        start = request.POST.get("start")
        days = int(request.POST.get("days", 7))
        max_shifts_per_week = int(request.POST.get("max_shifts_per_week", 5))
        confirm_overwrite = request.POST.get("confirm_overwrite")

        # Before delegating to the management command, check for overbooked dates
        from datetime import timedelta
        from django.core.management import call_command

        # read threshold from admin-editable RosterConfig if present
        try:
            from .models import RosterConfig

            cfg = RosterConfig.get_solo()
            OVERBOOK_THRESHOLD = cfg.overbook_threshold if cfg is not None else 6
        except Exception:
            OVERBOOK_THRESHOLD = 6

        s = date.fromisoformat(start)
        date_list = [s + timedelta(days=i) for i in range(days)]
        overbooked = []
        for d in date_list:
            holiday_ids = set(Holiday.objects.filter(start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("staff_id", flat=True))
            leave_ids = set(Leave.objects.filter(start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("staff_id", flat=True))
            dayoff_ids = set(DayOffRequest.objects.filter(date=d, status="APPROVED").values_list("staff_id", flat=True))
            combined_ids = holiday_ids.union(leave_ids).union(dayoff_ids)
            # Also detect staff who have existing assignments overlapping the holiday/leave ranges (avoid double booking)
            problem_staff = set()
            for staff_id in combined_ids:
                # find any Holiday/Leave covering this date for this staff
                has_holidays = Holiday.objects.filter(staff_id=staff_id, start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("start_date", "end_date")
                for sstart, send in has_holidays:
                    if ShiftAssignment.objects.filter(staff_id=staff_id, date__gte=sstart, date__lte=send).exists():
                        problem_staff.add(staff_id)
                has_leaves = Leave.objects.filter(staff_id=staff_id, start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("start_date", "end_date")
                for sstart, send in has_leaves:
                    if ShiftAssignment.objects.filter(staff_id=staff_id, date__gte=sstart, date__lte=send).exists():
                        problem_staff.add(staff_id)

            total = len(combined_ids)
            if total > OVERBOOK_THRESHOLD or problem_staff:
                # include note about problem_staff if present
                overbooked.append((d, total, problem_staff))

        if overbooked:
            # Separate concerns: overbooked counts vs staff who are double-booked (already assigned during their approved time off)
            overbook_lines = []
            doublebook_lines = []
            for item in overbooked:
                if len(item) == 2:
                    d, count = item
                    overbook_lines.append(f"{d.isoformat()}: {count} approved requests")
                else:
                    d, count, problem_staff = item
                    overbook_lines.append(f"{d.isoformat()}: {count} approved requests")
                    if problem_staff:
                        names = list(Staff.objects.filter(pk__in=problem_staff).values_list("full_name", flat=True))
                        ps = ", ".join(names)
                        doublebook_lines.append(f"{d.isoformat()}: {ps}")

            # show overbooked dates as an error
            if overbook_lines:
                messages.error(request, "Roster generation blocked: the following dates exceed the allowed number of approved time-off requests: %s" % ("; ".join(overbook_lines)))

            # show double-booked staff as a separate, less severe warning
            if doublebook_lines:
                messages.warning(request, "Conflicts found: some staff already have assignments during their approved time off (date: staff): %s" % ("; ".join(doublebook_lines)))

            return redirect(reverse("rosters:generate"))

        # check for existing rosters overlapping this period
        end = s + timedelta(days=days - 1)
        overlapping = list(Roster.objects.filter(start_date__lte=end, end_date__gte=s))
        if overlapping and not confirm_overwrite:
            messages.info(request, "Overlapping rosters detected; confirm overwrite to proceed.")
            return redirect(reverse("rosters:generate"))

        if overlapping and confirm_overwrite:
            # delete overlapping rosters (and their assignments)
            for r in overlapping:
                r.delete()

        # call management command programmatically
        call_command("generate_roster", f"--start={start}", f"--days={days}", f"--max-shifts={max_shifts_per_week}")
        messages.success(request, "Roster generated successfully")
        return redirect(reverse("rosters:generate"))


class RosterDetailView(View):
    template_name = "rosters/detail.html"

    def get(self, request, pk):
        roster = get_object_or_404(Roster, pk=pk)
        shift_groups = ShiftGroup.objects.filter(is_active=True)

        # Optional filter
        sg = request.GET.get("shift_group")
        assignments = roster.assignments.all()
        if sg:
            assignments = assignments.filter(shift_group_id=sg)

        # Build date list
        from datetime import timedelta
        date_list = []
        d = roster.start_date
        while d <= roster.end_date:
            date_list.append(d)
            d += timedelta(days=1)

        # Staff shown = all active
        staff_list = list(Staff.objects.filter(active=True).order_by("full_name"))

        # Build assign map
        from collections import defaultdict
        assign_map = defaultdict(dict)
        for a in assignments.select_related("staff", "shift_group"):
            assign_map[a.date][a.staff.id] = a

        # ==============================
        # LOAD Holidays / Leave
        # ==============================
        from collections import defaultdict as dd
        holiday_by_staff = dd(set)
        leave_by_staff = dd(set)

        hol_qs = Holiday.objects.filter(
            start_date__lte=roster.end_date,
            end_date__gte=roster.start_date,
            status="APPROVED"
        )
        for h in hol_qs:
            for dt in date_list:
                if h.start_date <= dt <= h.end_date:
                    holiday_by_staff[h.staff_id].add(dt)

        lv_qs = Leave.objects.filter(
            start_date__lte=roster.end_date,
            end_date__gte=roster.start_date,
            status="APPROVED"
        )
        for lv in lv_qs:
            for dt in date_list:
                if lv.start_date <= dt <= lv.end_date:
                    leave_by_staff[lv.staff_id].add(dt)

        # ==============================
        # VIEW-SIDE DAY-OFF DETECTION
        # ==============================
        # NEW RULE:
        # If a staff has NO ASSIGNMENT on a date AND it is not holiday/leave
        # → treat it as DAY OFF.
        #
        # DayOffRequest (approved) still overrides everything.
        # ==============================

        approved_dor = set(
            DayOffRequest.objects.filter(
                date__in=date_list,
                status="APPROVED"
            ).values_list("staff_id", "date")
        )

        def is_explicit_dor(sid, dt):
            return (sid, dt) in approved_dor

        # Build rows for template
        rows = []
        for s in staff_list:
            sid = s.id
            row = []
            for dt in date_list:

                a = assign_map.get(dt, {}).get(sid)
                is_hol = dt in holiday_by_staff[sid]
                is_lea = dt in leave_by_staff[sid]

                # Explicit DayOffRequest → Day Off
                if is_explicit_dor(sid, dt):
                    is_day_off = True
                # No assignment + no holiday + no leave → Day Off
                elif a is None and not is_hol and not is_lea:
                    is_day_off = True
                else:
                    is_day_off = False

                row.append((dt, a, is_hol, is_lea, is_day_off))

            rows.append((s, row))

        # Coverage table (unchanged)
        coverage_rows = []
        explicit_requirements = {
            'night': (7, 4),
            'evening': (7, 4),
            'morning 7:30': (1, 0),
            'morning 8h': (12, 11),
            'morning 9h': (3, 2),
        }
        for sg_obj in shift_groups:
            cells = []
            sn = sg_obj.shift_name.lower()
            for dt in date_list:
                cnt = roster.assignments.filter(shift_group=sg_obj, date=dt).count()
                we = dt.weekday() >= 5
                req = None
                for key, (wk_req, we_req) in explicit_requirements.items():
                    if key in sn:
                        req = we_req if we else wk_req
                        break
                if req is None:
                    req = sg_obj.required_weekend if we else sg_obj.required_weekday
                diff = req - cnt
                cells.append((cnt, req, diff, abs(diff)))
            coverage_rows.append((sg_obj, cells))

        # Eligible staff (unchanged)
        eligible_staff_by_sg = {}
        for sg_obj in shift_groups:
            eligible_staff_by_sg[sg_obj.pk] = list(
                Staff.objects.filter(active=True, shift_groups=sg_obj)
                .order_by("full_name")
                .values("pk", "full_name")
            )

        return render(
            request,
            self.template_name,
            {
                "roster": roster,
                "shift_groups": shift_groups,
                "date_list": date_list,
                "rows": rows,
                "coverage_rows": coverage_rows,
                "selected_shift": int(sg) if sg else None,
                "eligible_staff_by_sg": eligible_staff_by_sg,
            },
        )


class AssignmentEditView(View):
    """AJAX endpoint to reassign an assignment to a different staff member."""

    def post(self, request, pk):
        try:
            assignment = ShiftAssignment.objects.select_related("shift_group").get(pk=pk)
        except ShiftAssignment.DoesNotExist:
            return JsonResponse({"error": "assignment_not_found"}, status=404)

        staff_id = request.POST.get("staff_id")
        if not staff_id:
            return JsonResponse({"error": "missing_staff_id"}, status=400)

        try:
            new_staff = Staff.objects.get(pk=staff_id, active=True)
        except Staff.DoesNotExist:
            return JsonResponse({"error": "staff_not_found_or_inactive"}, status=404)

        # Validate the staff can work this shift_group
        allowed = new_staff.shift_groups.filter(pk=assignment.shift_group_id).exists()
        if not allowed:
            return JsonResponse({"error": "staff_cannot_work_shift"}, status=400)

        # Check for uniqueness: ensure no other assignment exists for same date+shift_group
        conflict = ShiftAssignment.objects.filter(date=assignment.date, shift_group=assignment.shift_group).exclude(pk=assignment.pk).exists()
        # uniqueness constraint is per date+shift_group, but we are only swapping staff on this assignment,
        # so conflict should not occur unless multiple slots per shift were modelled differently; skip conflict check.

        assignment.staff = new_staff
        assignment.save()

        return JsonResponse({
            "success": True,
            "assignment_id": assignment.pk,
            "staff_name": new_staff.full_name,
            "staff_id": new_staff.pk,
        })


class CheckGenerateView(View):
    """AJAX endpoint to check for overlaps and overbook/doublebook issues before generation."""

    def post(self, request):
        start = request.POST.get("start")
        days = int(request.POST.get("days", 7))
        from datetime import timedelta

        s = date.fromisoformat(start)
        end = s + timedelta(days=days - 1)

        # overlapping rosters
        overlapping = list(Roster.objects.filter(start_date__lte=end, end_date__gte=s).values("pk", "start_date", "end_date"))

        # reuse same overbook/doublebook logic as generate view
        date_list = [s + timedelta(days=i) for i in range(days)]
        overbooked = []
        try:
            from .models import RosterConfig
            cfg = RosterConfig.get_solo()
            OVERBOOK_THRESHOLD = cfg.overbook_threshold if cfg is not None else 6
        except Exception:
            OVERBOOK_THRESHOLD = 6

        for d in date_list:
            holiday_ids = set(Holiday.objects.filter(start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("staff_id", flat=True))
            leave_ids = set(Leave.objects.filter(start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("staff_id", flat=True))
            dayoff_ids = set(DayOffRequest.objects.filter(date=d, status="APPROVED").values_list("staff_id", flat=True))
            combined_ids = holiday_ids.union(leave_ids).union(dayoff_ids)

            problem_staff = set()
            for staff_id in combined_ids:
                has_holidays = Holiday.objects.filter(staff_id=staff_id, start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("start_date", "end_date")
                for sstart, send in has_holidays:
                    if ShiftAssignment.objects.filter(staff_id=staff_id, date__gte=sstart, date__lte=send).exists():
                        problem_staff.add(staff_id)
                has_leaves = Leave.objects.filter(staff_id=staff_id, start_date__lte=d, end_date__gte=d, status="APPROVED").values_list("start_date", "end_date")
                for sstart, send in has_leaves:
                    if ShiftAssignment.objects.filter(staff_id=staff_id, date__gte=sstart, date__lte=send).exists():
                        problem_staff.add(staff_id)

            total = len(combined_ids)
            if total > OVERBOOK_THRESHOLD or problem_staff:
                overbooked.append({"date": d.isoformat(), "count": total, "problem_staff": list(problem_staff)})

        return JsonResponse({"overlapping": overlapping, "issues": overbooked})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class DeleteRosterView(View):
    """Delete a roster. Only staff users allowed (admin). POST only."""

    def post(self, request, pk):
        roster = get_object_or_404(Roster, pk=pk)
        roster_label = str(roster)
        roster.delete()
        messages.success(request, f"Deleted roster {roster_label}")
        return redirect(reverse("rosters:generate"))


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class PersistAutoDayOffsView(View):
    """Compute auto day-offs for a roster and persist them as APPROVED DayOffRequest records.

    Idempotent: will get_or_create per (staff, date) and set status=APPROVED and approved_by/request.user.
    """

    def post(self, request, pk):
        roster = get_object_or_404(Roster, pk=pk)

        # Recompute day_offs_by_staff using same rules as RosterDetailView
        from collections import defaultdict as _defaultdict
        from datetime import timedelta

        date_list = []
        d = roster.start_date
        while d <= roster.end_date:
            date_list.append(d)
            d += timedelta(days=1)

        assignments = roster.assignments.select_related('staff')
        assign_map = _defaultdict(dict)
        for a in assignments:
            assign_map[a.date][a.staff.id] = a

        # holidays and leaves
        holiday_by_staff = _defaultdict(set)
        for h in Holiday.objects.filter(start_date__lte=roster.end_date, end_date__gte=roster.start_date, status="APPROVED"):
            for dd in date_list:
                if h.start_date <= dd <= h.end_date:
                    holiday_by_staff[h.staff_id].add(dd)

        leave_by_staff = _defaultdict(set)
        for lv in Leave.objects.filter(start_date__lte=roster.end_date, end_date__gte=roster.start_date, status="APPROVED"):
            for dd in date_list:
                if lv.start_date <= dd <= lv.end_date:
                    leave_by_staff[lv.staff_id].add(dd)

        # start with explicit approved DayOffRequest
        day_offs_by_staff = _defaultdict(set)
        for dor in DayOffRequest.objects.filter(date__in=date_list, status="APPROVED"):
            day_offs_by_staff[dor.staff_id].add(dor.date)

        # weekend group
        from staff_management.models import WeekendGroup, Staff as StaffModel
        week_number = ((roster.start_date.day - 1) // 7) + 1
        wg = WeekendGroup.objects.filter(number=week_number).first()
        weekend_staff_ids = set()
        if wg is not None:
            weekend_staff_ids = set(StaffModel.objects.filter(weekend_group=wg).values_list('id', flat=True))
            for dd in date_list:
                if dd.weekday() >= 5:
                    for sid in weekend_staff_ids:
                        day_offs_by_staff[sid].add(dd)

        # compute per-staff free dates and cluster
        staff_set = set(a.staff for a in assignments)
        for s in staff_set:
            sid = s.id
            free_dates = [dd for dd in date_list if assign_map.get(dd, {}).get(sid) is None and dd not in day_offs_by_staff[sid] and dd not in holiday_by_staff[sid] and dd not in leave_by_staff[sid]]
            if not free_dates:
                continue
            runs = []
            run = []
            prev = None
            for dd in free_dates:
                if prev is None or (dd - prev).days == 1:
                    run.append(dd)
                else:
                    if run:
                        runs.append(run)
                    run = [dd]
                prev = dd
            if run:
                runs.append(run)

            for r in runs:
                if len(r) >= 2:
                    for dd in r:
                        day_offs_by_staff[sid].add(dd)

            singles = [r[0] for r in runs if len(r) == 1]
            for dd in singles:
                paired = False
                for candidate in (dd + timedelta(days=1), dd - timedelta(days=1)):
                    if candidate in free_dates and candidate not in day_offs_by_staff[sid] and candidate in date_list:
                        day_offs_by_staff[sid].add(dd)
                        day_offs_by_staff[sid].add(candidate)
                        paired = True
                        break

        # Persist DayOffRequest rows: use get_or_create; set status APPROVED and approved_by/request.user
        created = 0
        updated = 0
        for sid, dates in day_offs_by_staff.items():
            for dd in dates:
                # skip if this date is a holiday or leave for the staff (these take precedence)
                if dd in holiday_by_staff.get(sid, set()) or dd in leave_by_staff.get(sid, set()):
                    continue
                obj, was_created = DayOffRequest.objects.get_or_create(staff_id=sid, date=dd, defaults={
                    'status': 'APPROVED',
                    'created_by': request.user,
                    'approved_by': request.user,
                    'comment': 'auto-persisted by roster',
                })
                if was_created:
                    created += 1
                else:
                    # ensure it's approved
                    if obj.status != 'APPROVED' or obj.approved_by_id is None:
                        obj.status = 'APPROVED'
                        obj.approved_by = request.user
                        # mark as auto-persisted so it can be identified for undo
                        if not obj.comment:
                            obj.comment = 'auto-persisted by roster'
                        obj.save()
                        updated += 1

        messages.success(request, f"Persisted {created} new DayOffRequest(s), updated {updated} existing.")
        return redirect(reverse('rosters:detail', args=[roster.pk]))


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class RevertAutoDayOffsView(View):
    """Remove auto-persisted DayOffRequest rows for a roster (undo).

    This deletes DayOffRequest records whose comment equals the auto marker within the roster date range.
    """

    def post(self, request, pk):
        roster = get_object_or_404(Roster, pk=pk)
        from datetime import timedelta
        date_list = []
        d = roster.start_date
        while d <= roster.end_date:
            date_list.append(d)
            d += timedelta(days=1)

        qs = DayOffRequest.objects.filter(date__in=date_list, comment='auto-persisted by roster')
        count = qs.count()
        qs.delete()
        messages.success(request, f"Reverted {count} auto-persisted DayOffRequest(s).")
        return redirect(reverse('rosters:detail', args=[roster.pk]))

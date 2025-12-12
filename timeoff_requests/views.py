from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from operator import itemgetter
from datetime import datetime

from .models import Holiday, Leave, DayOffRequest, RequestStatus
from .forms import HolidayForm, LeaveForm, DayOffRequestForm


def _parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


# ===================== Unified list with filters =====================

@login_required
def requests_all(request):
    f_status = request.GET.get("status", "").strip()
    f_staff  = request.GET.get("staff", "").strip()
    f_user   = request.GET.get("user", "").strip()
    f_from   = request.GET.get("from", "").strip()
    f_to     = request.GET.get("to", "").strip()
    d_from   = _parse_date(f_from)
    d_to     = _parse_date(f_to)

    rows = []

    hol_qs = Holiday.objects.select_related("staff", "created_by")
    lev_qs = Leave.objects.select_related("staff", "created_by")
    day_qs = DayOffRequest.objects.select_related("staff", "created_by")

    if f_status:
        hol_qs = hol_qs.filter(status=f_status)
        lev_qs = lev_qs.filter(status=f_status)
        day_qs = day_qs.filter(status=f_status)
    if f_staff:
        filt = Q(staff__full_name__icontains=f_staff) | Q(staff__employee_id__icontains=f_staff)
        hol_qs = hol_qs.filter(filt)
        lev_qs = lev_qs.filter(filt)
        day_qs = day_qs.filter(filt)
    if f_user:
        hol_qs = hol_qs.filter(created_by__username__icontains=f_user)
        lev_qs = lev_qs.filter(created_by__username__icontains=f_user)
        day_qs = day_qs.filter(created_by__username__icontains=f_user)
    if d_from:
        hol_qs = hol_qs.filter(created_at__date__gte=d_from)
        lev_qs = lev_qs.filter(created_at__date__gte=d_from)
        day_qs = day_qs.filter(created_at__date__gte=d_from)
    if d_to:
        hol_qs = hol_qs.filter(created_at__date__lte=d_to)
        lev_qs = lev_qs.filter(created_at__date__lte=d_to)
        day_qs = day_qs.filter(created_at__date__lte=d_to)

    for h in hol_qs:
        rows.append({
            "type": "Holiday",
            "id": h.id,
            "staff_name": h.staff.full_name,
            "employee_id": h.staff.employee_id,
            "requested_date": h.created_at,
            "start_date": h.start_date,
            "end_date": h.end_date,
            "status": h.status,
            "status_label": h.get_status_display(),
            "comment": getattr(h, "comment", ""),  # renamed
            "user": getattr(h.created_by, "username", "—"),
            "edit_url_name": "timeoff_requests:holiday_edit",
            "delete_url_name": "timeoff_requests:holiday_delete",
            "approve_url_name": "timeoff_requests:holiday_approve",
            "bulk_checkbox": True,
        })

    for l in lev_qs:
        rows.append({
            "type": f"Leave • {l.get_leave_type_display()}",
            "id": l.id,
            "staff_name": l.staff.full_name,
            "employee_id": l.staff.employee_id,
            "requested_date": l.created_at,
            "start_date": l.start_date,
            "end_date": l.end_date,
            "status": l.status,
            "status_label": l.get_status_display(),
            "comment": getattr(l, "comment", ""),
            "user": getattr(l.created_by, "username", "—"),
            "edit_url_name": "timeoff_requests:leave_edit",
            "delete_url_name": "timeoff_requests:leave_delete",
            "approve_url_name": "timeoff_requests:leave_approve",
            "bulk_checkbox": False,
        })

    for d in day_qs:
        rows.append({
            "type": "Day Off",
            "id": d.id,
            "staff_name": d.staff.full_name,
            "employee_id": d.staff.employee_id,
            "requested_date": d.created_at,
            "start_date": d.date,
            "end_date": d.date,
            "status": d.status,
            "status_label": d.get_status_display(),
            "comment": getattr(d, "comment", ""),
            "user": getattr(d.created_by, "username", "—"),
            "edit_url_name": "timeoff_requests:dayoff_edit",
            "delete_url_name": "timeoff_requests:dayoff_delete",
            "approve_url_name": "timeoff_requests:dayoff_approve",
            "bulk_checkbox": False,
        })

    rows.sort(key=itemgetter("requested_date"), reverse=True)
    return render(request, "timeoff/requests_list.html", {
        "rows": rows,
        "filters": {"status": f_status, "staff": f_staff, "user": f_user, "from": f_from, "to": f_to},
    })


# ===================== Holidays CRUD =====================

@login_required
def holiday_create(request):
    form = HolidayForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        # ensure Pending on create
        obj.status = RequestStatus.PENDING
        obj.save()
        messages.success(request, "Holiday created.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": "Add Holiday"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def holiday_edit(request, pk):
    obj = get_object_or_404(Holiday, pk=pk)
    form = HolidayForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Holiday updated.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": f"Edit Holiday – {obj.staff}"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def holiday_delete(request, pk):
    obj = get_object_or_404(Holiday, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Holiday deleted.")
        return redirect("timeoff_requests:requests_all")
    return render(request, "timeoff/confirm_delete.html", {"obj": obj, "title": "Delete Holiday"})


# ===================== Leaves CRUD =====================

@login_required
def leave_create(request):
    form = LeaveForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.status = RequestStatus.PENDING
        obj.save()
        messages.success(request, "Leave created.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": "Add Leave"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def leave_edit(request, pk):
    obj = get_object_or_404(Leave, pk=pk)
    form = LeaveForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Leave updated.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": f"Edit Leave – {obj.staff}"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def leave_delete(request, pk):
    obj = get_object_or_404(Leave, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Leave deleted.")
        return redirect("timeoff_requests:requests_all")
    return render(request, "timeoff/confirm_delete.html", {"obj": obj, "title": "Delete Leave"})


# ===================== Day Off CRUD =====================

@login_required
def dayoff_request_create(request):
    form = DayOffRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.status = RequestStatus.PENDING
        obj.save()
        messages.success(request, "Day-off request created.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": "Add Day Off Request"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def dayoff_edit(request, pk):
    obj = get_object_or_404(DayOffRequest, pk=pk)
    form = DayOffRequestForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Day-off request updated.")
        return redirect("timeoff_requests:requests_all")
    ctx = {"form": form, "title": f"Edit Day Off – {obj.staff} ({obj.date})"}
    if hasattr(form, 'staff_options'):
        ctx['form'].staff_text = form.fields['staff_text']
        ctx['form'].staff_options = form.staff_options
    return render(request, "timeoff/form.html", ctx)

@login_required
def dayoff_delete(request, pk):
    obj = get_object_or_404(DayOffRequest, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Day-off request deleted.")
        return redirect("timeoff_requests:requests_all")
    return render(request, "timeoff/confirm_delete.html", {"obj": obj, "title": "Delete Day Off Request"})


# ===================== Approvals & bulk (permissions) =====================

@permission_required("timeoff_requests.approve_holiday")
def holiday_approve(request, pk):
    obj = get_object_or_404(Holiday, pk=pk)
    if not obj.is_approved:
        obj.approve(request.user)          # uses helper; sets approved_by/at
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Holiday approved.")
    return redirect("timeoff_requests:requests_all")

@permission_required("timeoff_requests.approve_leave")
def leave_approve(request, pk):
    obj = get_object_or_404(Leave, pk=pk)
    if not obj.is_approved:
        obj.approve(request.user)
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Leave approved.")
    return redirect("timeoff_requests:requests_all")

@permission_required("timeoff_requests.approve_dayoff")
def dayoff_approve(request, pk):
    obj = get_object_or_404(DayOffRequest, pk=pk)
    if not obj.is_pending:
        # allow re-approval flows; but typically you'd block unless Pending
        pass
    if obj.status != RequestStatus.APPROVED:
        obj.approve(request.user)
        obj.updated_by = request.user
        obj.save()
        messages.success(request, "Day off approved.")
    return redirect("timeoff_requests:requests_all")

@permission_required("timeoff_requests.approve_holiday")
def holidays_bulk_approve(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        qs = Holiday.objects.filter(id__in=ids).exclude(status=RequestStatus.APPROVED)
        updated = 0
        for h in qs:
            h.approve(request.user)
            h.updated_by = request.user
            h.save()
            updated += 1
        messages.success(request, f"Approved {updated} holiday request(s).")
    return redirect("timeoff_requests:requests_all")
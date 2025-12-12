from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Staff, WeekendGroup, ShiftGroup
from .forms import StaffForm, WeekendGroupForm, ShiftGroupForm

@login_required
def staff_list(request):
    q = request.GET.get('q', '').strip()
    items = (Staff.objects
             .all()
             .prefetch_related('shift_groups')
             .order_by('full_name'))
    if q:
        items = items.filter(full_name__icontains=q)
    return render(request, 'staff/staff_list.html', {'items': items, 'q': q})

@login_required
def staff_create(request):
    form = StaffForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()
        form.save_m2m()
        return redirect('staff_management:staff_list')
    return render(request, 'staff/form.html', {'form': form, 'title': 'Add Staff'})

@login_required
def staff_edit(request, pk):
    obj = get_object_or_404(Staff, pk=pk)
    form = StaffForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.updated_by = request.user
        obj.save()
        form.save_m2m()
        return redirect('staff_management:staff_list')
    return render(request, 'staff/form.html', {'form': form, 'title': f'Edit {obj.full_name}'})

@login_required
def staff_delete(request, pk):
    obj = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('staff_management:staff_list')
    return render(request, 'staff/confirm_delete.html', {'obj': obj, 'title': f'Delete {obj.full_name}'})


# -------- Weekends Groups CRUD --------
@login_required
def weekend_groups(request):
    items = WeekendGroup.objects.order_by("number")
    return render(request, "staff/weekend_groups.html", {"items": items})

@login_required
def weekend_group_add(request):
    if request.method == "POST":
        form = WeekendGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff_management:weekend_groups")
    else:
        form = WeekendGroupForm()
    return render(request, "staff/form.html", {"form": form, "title": "Add Weekend Group"})

@login_required
def weekend_group_edit(request, pk):
    obj = get_object_or_404(WeekendGroup, pk=pk)
    if request.method == "POST":
        form = WeekendGroupForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("staff_management:weekend_groups")
    else:
        form = WeekendGroupForm(instance=obj)
    return render(request, "staff/form.html", {"form": form, "title": "Edit Weekend Group"})

@login_required
def weekend_group_delete(request, pk):
    obj = get_object_or_404(WeekendGroup, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("staff_management:weekend_groups")
    return render(
        request,
        "staff/confirm_delete.html",
        {"title": "Weekend Group", "obj": obj},   # no cancel_url here
    )
# -------- Shift Groups CRUD --------

@login_required
def shiftgroup_list(request):
    items = ShiftGroup.objects.all().order_by("shift_name")
    return render(request, "staff/shift_groups.html", {"items": items})

@login_required
def shiftgroup_edit(request, pk=None):
    obj = ShiftGroup.objects.filter(pk=pk).first()
    form = ShiftGroupForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("staff_management:shiftgroup_list")
    title = "Edit Shift Group" if obj else "Add Shift Group"
    return render(request, "staff/form.html", {"form": form, "title": title})

@login_required
def shiftgroup_delete(request, pk):
    obj = get_object_or_404(ShiftGroup, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("staff_management:shiftgroup_list")
    return render(request, "staff/confirm_delete.html", {"obj": obj, "title": f"Delete {obj.shift_name}"})
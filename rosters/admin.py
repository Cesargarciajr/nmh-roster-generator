from django.contrib import admin

from .models import Roster, ShiftAssignment, RosterConfig


@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "created_at")


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ("date", "shift_group", "staff")


@admin.register(RosterConfig)
class RosterConfigAdmin(admin.ModelAdmin):
    list_display = ("overbook_threshold",)
    change_list_template = "admin/rosters/rosterconfig_changelist.html"

    def has_add_permission(self, request):
        # allow add only if no config exists
        return not RosterConfig.objects.exists()

    def changelist_view(self, request, extra_context=None):
        # if a config exists, redirect straight to its change view for convenience
        qs = RosterConfig.objects.all()
        if qs.count() == 1:
            obj = qs.first()
            from django.shortcuts import redirect
            return redirect(f"../{obj.pk}/change/")
        return super().changelist_view(request, extra_context=extra_context)

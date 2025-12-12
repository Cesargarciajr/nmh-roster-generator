from django.contrib import admin
from . import models as m

@admin.register(m.ShiftGroup)
class ShiftGroupAdmin(admin.ModelAdmin):
    list_display = ("shift_name", "is_active", "description")
    list_editable = ("is_active",)
    search_fields = ("shift_name", "description")

@admin.register(m.WeekendGroup)
class WeekendGroupAdmin(admin.ModelAdmin):
    list_display = ("number", "name")

@admin.register(m.Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display  = ("full_name", "employee_id", "active", "gender", "created_by", "created_at")
    list_filter   = ("active", "gender", "weekend_group", "shift_groups")
    search_fields = ("full_name", "employee_id")
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")
    filter_horizontal = ("shift_groups",)  # nice dual-list widget in admin
from django.contrib import admin
from . import models as m

@admin.register(m.Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("staff","start_date","end_date","status","created_by")
    list_filter = ("status",)
    readonly_fields = ("created_by","updated_by","created_at","updated_at","approved_by","approved_at")

@admin.register(m.Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("staff","leave_type","start_date","end_date","status","created_by")
    list_filter = ("leave_type","status")
    readonly_fields = ("created_by","updated_by","created_at","updated_at","approved_by","approved_at")

@admin.register(m.DayOffRequest)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ("staff","date","status","created_by")
    list_filter = ("status",)
    readonly_fields = ("created_by","updated_by","created_at","updated_at","approved_by","approved_at")

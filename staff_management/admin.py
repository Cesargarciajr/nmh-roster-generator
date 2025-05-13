from django.contrib import admin
from .models import Staff

class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_name', 'weekend_group', 'shift_period_assigned', 'gender', 'status']
    search_fields = ['staff_name', 'assigned_unit', 'gender', 'status']
    list_filter = ['weekend_group', 'shift_period_assigned', 'contract_type', 'status']

admin.site.register(Staff, StaffAdmin)

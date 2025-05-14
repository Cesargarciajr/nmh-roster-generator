from django.contrib import admin
from django import forms
from .models import Staff, WeekendGroup, Unit, WorkShift

# --------------------------------------------
# Custom form for the Staff model in admin
# --------------------------------------------
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'  # Use all model fields in the admin form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom CSS classes to these fields for easier targeting/styling in templates or JS
        self.fields['unit_restrictions'].widget.attrs.update({'class': 'unit-restrictions-widget'})
        self.fields['assigned_unit'].widget.attrs.update({'class': 'assigned-unit-widget'})


# --------------------------------------------
# Custom admin interface for the Staff model
# --------------------------------------------
class StaffAdmin(admin.ModelAdmin):
    form = StaffForm  # Use the customized form above

    # Fields to display in the staff list view in Django admin
    list_display = ['staff_name', 'gender', 'get_work_shifts', 'status']

    # Enable search functionality in admin based on these fields
    search_fields = ['staff_name', 'gender', 'status']

    # Add filters in the sidebar for these fields
    list_filter = ['contract_type', 'status']

    # Use a more user-friendly multi-select widget for ManyToMany fields
    filter_horizontal = ['weekend_groups', 'work_shifts', 'unit_restrictions', 'assigned_unit']

    # Custom method to show related WorkShifts in a readable format in the list view
    def get_work_shifts(self, obj):
        return ", ".join([shift.work_shift for shift in obj.work_shifts.all()])
    get_work_shifts.short_description = 'Work Shifts'  # Column name in admin list view

    # --------------------------------------------
    # Save model instance before handling M2M fields
    # --------------------------------------------
    def save_model(self, request, obj, form, change):
        # Ensure the instance is saved to the database and has a primary key
        obj.save()

    # --------------------------------------------
    # Save M2M relationships after the main instance is saved
    # --------------------------------------------
    def save_related(self, request, form, formsets, change):
        # Save many-to-many data only after the primary object exists
        form.save_m2m()
        super().save_related(request, form, formsets, change)


# --------------------------------------------
# Register models in the Django admin interface
# --------------------------------------------
admin.site.register(Staff, StaffAdmin)         # Register Staff model with the custom admin
admin.site.register(WeekendGroup)              # Basic registration for related models
admin.site.register(Unit)
admin.site.register(WorkShift)

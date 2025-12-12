from django import forms
from .models import Staff, WeekendGroup, ShiftGroup

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "full_name", "employee_id", "gender", "active",
            "shift_groups",               # now M2M
            "can_do_weekend_morning", "must_do_weekly_evening",
            "weekend_group",
        ]
        widgets = {
            "shift_groups": forms.CheckboxSelectMultiple,
        }


class WeekendGroupForm(forms.ModelForm):
    class Meta:
        model = WeekendGroup
        fields = ["number", "name"]

class ShiftGroupForm(forms.ModelForm):
    class Meta:
        model = ShiftGroup
        fields = ["shift_name", "is_active", "description"]
# timeoff_requests/forms.py
from django import forms
from staff_management.models import Staff
from .models import Holiday, Leave, DayOffRequest

def _staff_queryset():
    # Only active staff, ordered by name
    return Staff.objects.filter(active=True).order_by("full_name", "employee_id")

def _label_staff(obj: Staff) -> str:
    # Nice label in the dropdown
    eid = f" ({obj.employee_id})" if obj.employee_id else ""
    return f"{obj.full_name}{eid}"

class StaffSelectMixin:
    """Adds a 'staff' ModelChoiceField with a nice label."""
    def _init_staff_field(self):
        self.fields["staff"] = forms.ModelChoiceField(
            queryset=_staff_queryset(),
            required=True,
            label="Staff",
            widget=forms.Select(attrs={"class": "select is-fullwidth"}),  # Bulma-friendly class
        )
        # Pretty labels for each option
        self.fields["staff"].label_from_instance = _label_staff
        # Add a text input for autocomplete/lookup in templates (optional)
        self.fields["staff_text"] = forms.CharField(
            required=False,
            label="Staff",
            widget=forms.TextInput(attrs={"class": "input", "list": "staff-options"}),
        )
        # expose options for datalist in templates
        self.staff_options = [ _label_staff(s) for s in _staff_queryset() ]

class HolidayForm(StaffSelectMixin, forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ["staff", "start_date", "end_date", "comment"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "input"}),
            "end_date":   forms.DateInput(attrs={"type": "date", "class": "input"}),
            "comment":    forms.Textarea(attrs={"rows": 3, "class": "textarea", "placeholder": "Comment (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_staff_field()
        # ensure widgets have Bulma classes when not explicitly set
        for fname, f in self.fields.items():
            cls = f.widget.attrs.get('class')
            if cls:
                continue
            # pick sensible default
            if isinstance(f.widget, forms.Textarea):
                f.widget.attrs['class'] = 'textarea'
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'select is-fullwidth'
            else:
                f.widget.attrs['class'] = 'input'

class LeaveForm(StaffSelectMixin, forms.ModelForm):
    class Meta:
        model = Leave
        fields = ["staff", "leave_type", "start_date", "end_date", "comment"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "select is-fullwidth"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "input"}),
            "end_date":   forms.DateInput(attrs={"type": "date", "class": "input"}),
            "comment":    forms.Textarea(attrs={"rows": 3, "class": "textarea", "placeholder": "Comment (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_staff_field()
        for fname, f in self.fields.items():
            cls = f.widget.attrs.get('class')
            if cls:
                continue
            if isinstance(f.widget, forms.Textarea):
                f.widget.attrs['class'] = 'textarea'
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'select is-fullwidth'
            else:
                f.widget.attrs['class'] = 'input'

class DayOffRequestForm(StaffSelectMixin, forms.ModelForm):
    class Meta:
        model = DayOffRequest
        fields = ["staff", "date", "comment"]
        widgets = {
            "date":    forms.DateInput(attrs={"type": "date", "class": "input"}),
            "comment": forms.Textarea(attrs={"rows": 3, "class": "textarea", "placeholder": "Comment (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_staff_field()
        for fname, f in self.fields.items():
            cls = f.widget.attrs.get('class')
            if cls:
                continue
            if isinstance(f.widget, forms.Textarea):
                f.widget.attrs['class'] = 'textarea'
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'select is-fullwidth'
            else:
                f.widget.attrs['class'] = 'input'

# timeoff_requests/templatetags/form_extras.py
from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """Usage: {{ field|add_class:'input' }}"""
    try:
        existing = field.field.widget.attrs.get("class", "")
        new_class = (existing + " " + css).strip()
        return field.as_widget(attrs={**field.field.widget.attrs, "class": new_class})
    except Exception:
        return field

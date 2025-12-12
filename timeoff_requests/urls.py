from django.urls import path
from . import views

app_name = "timeoff_requests"

urlpatterns = [
    # unified list
    path("", views.requests_all, name="requests_all"),

    # holidays
    path("holidays/add/", views.holiday_create, name="holiday_add"),
    path("holidays/<int:pk>/edit/", views.holiday_edit, name="holiday_edit"),
    path("holidays/<int:pk>/delete/", views.holiday_delete, name="holiday_delete"),
    path("holidays/<int:pk>/approve/", views.holiday_approve, name="holiday_approve"),
    path("holidays/bulk-approve/", views.holidays_bulk_approve, name="holidays_bulk_approve"),

    # leaves
    path("leaves/add/", views.leave_create, name="leave_add"),
    path("leaves/<int:pk>/edit/", views.leave_edit, name="leave_edit"),
    path("leaves/<int:pk>/delete/", views.leave_delete, name="leave_delete"),
    path("leaves/<int:pk>/approve/", views.leave_approve, name="leave_approve"),

    # day off
    path("dayoff/add/", views.dayoff_request_create, name="dayoff_add"),
    path("dayoff/<int:pk>/edit/", views.dayoff_edit, name="dayoff_edit"),          # <— updated
    path("dayoff/<int:pk>/delete/", views.dayoff_delete, name="dayoff_delete"),    # <— updated
    path("dayoff/<int:pk>/approve/", views.dayoff_approve, name="dayoff_approve"),
]

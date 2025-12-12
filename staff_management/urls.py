from django.urls import path
from . import views

app_name = 'staff_management'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('add/', views.staff_create, name='staff_add'),
    path('<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    path("weekend-groups/", views.weekend_groups, name="weekend_groups"),
    path("weekend-groups/add/", views.weekend_group_add, name="weekend_group_add"),
    path("weekend-groups/<int:pk>/edit/", views.weekend_group_edit, name="weekend_group_edit"),
    path("weekend-groups/<int:pk>/delete/", views.weekend_group_delete, name="weekend_group_delete"),
    path("shift-groups/", views.shiftgroup_list, name="shiftgroup_list"),
    path("shift-groups/edit/", views.shiftgroup_edit, name="shiftgroup_add"),
    path("shift-groups/<int:pk>/edit/", views.shiftgroup_edit, name="shiftgroup_edit"),
    path("shift-groups/<int:pk>/delete/", views.shiftgroup_delete, name="shiftgroup_delete"),
]
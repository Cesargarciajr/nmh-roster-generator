from django.urls import path
from . import views

urlpatterns = [
    # URL for the staff management page (viewing all staff)
    #path('staff_management/', views.staff_management, name='staff_management'),

    # URL for adding a new staff member
    path('add_staff/', views.add_staff, name='add_staff'),

    # URL for viewing details of a specific staff member
    #path('staff_details/<int:staff_id>/', views.staff_details, name='staff_details'),

]
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def index(request):
    return render(request, "index.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),  # root goes to index.html
    path("staff/", include("staff_management.urls")),
    path("accounts/", include("accounts.urls")),
    path("timeoff/", include("timeoff_requests.urls")),
    path("rosters/", include("rosters.urls")),
]

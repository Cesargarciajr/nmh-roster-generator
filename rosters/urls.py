from django.urls import path
from .views import GenerateRosterView, RosterDetailView
from .views import AssignmentEditView, CheckGenerateView
from .views import DeleteRosterView
from .views import PersistAutoDayOffsView
from .views import RevertAutoDayOffsView

app_name = "rosters"

urlpatterns = [
    path("generate/", GenerateRosterView.as_view(), name="generate"),
    path("check_generate/", CheckGenerateView.as_view(), name="check_generate"),
    path("<int:pk>/delete/", DeleteRosterView.as_view(), name="delete_roster"),
    path("<int:pk>/", RosterDetailView.as_view(), name="detail"),
    path("<int:pk>/persist_auto_dayoffs/", PersistAutoDayOffsView.as_view(), name="persist_auto_dayoffs"),
    path("<int:pk>/revert_auto_dayoffs/", RevertAutoDayOffsView.as_view(), name="revert_auto_dayoffs"),
    path("assignment/<int:pk>/edit/", AssignmentEditView.as_view(), name="assignment_edit"),
]

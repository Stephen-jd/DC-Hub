from django.urls import path
from .views import (
    AdminDashboardView,
    ManageStudentsView,
    ManageBatchesView,
    AssignTrainerBatchView,
    ExportStudentsCSVView,
    ImportStudentsCSVView
)

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("students/manage/", ManageStudentsView.as_view(), name="manage_students"),
    path("batches/manage/", ManageBatchesView.as_view(), name="manage_batches"),
    path("trainer/assign/", AssignTrainerBatchView.as_view(), name="assign_trainer_batch"),
    path("students/export/", ExportStudentsCSVView.as_view(), name="export_students"),
    path("students/import/", ImportStudentsCSVView.as_view(), name="import_students"),
]

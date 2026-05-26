from django.urls import path
from .views import (
    StudentDashboardView,
    StudentExamView,
    StudentProfileUpdateView,
    SendDoubtView,
    ApplyJobView
)

urlpatterns = [
    path("dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("exam/<int:assessment_id>/", StudentExamView.as_view(), name="student_exam"),
    path("profile/update/", StudentProfileUpdateView.as_view(), name="student_profile_update"),
    path("doubts/send/", SendDoubtView.as_view(), name="send_doubt"),
    path("job/<int:job_id>/apply/", ApplyJobView.as_view(), name="apply_job"),
]

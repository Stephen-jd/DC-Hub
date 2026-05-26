from django.urls import path
from .views import (
    BDDashboardView,
    BDStudentProfileView,
    PostJobView,
    BDMessageView,
    ShortlistCandidateView,
    RejectCandidateView
)

urlpatterns = [
    path("dashboard/", BDDashboardView.as_view(), name="bd_dashboard"),
    path("student/<int:student_id>/", BDStudentProfileView.as_view(), name="bd_student_profile"),
    path("job/post/", PostJobView.as_view(), name="post_job"),
    path("message/<int:student_id>/", BDMessageView.as_view(), name="bd_message_student"),
    path("application/shortlist/<int:app_id>/", ShortlistCandidateView.as_view(), name="shortlist_candidate"),
    path("application/reject/<int:app_id>/", RejectCandidateView.as_view(), name="reject_candidate"),
]

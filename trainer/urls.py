from django.urls import path
from .views import (
    TrainerDashboardView,
    UpdateSyllabusView,
    MockGraderView,
    DoubtReplyView
)

urlpatterns = [
    path("dashboard/", TrainerDashboardView.as_view(), name="trainer_dashboard"),
    path("syllabus/update/<int:item_id>/", UpdateSyllabusView.as_view(), name="update_syllabus"),
    path("mock/grade/", MockGraderView.as_view(), name="mock_grade"),
    path("doubt/reply/<int:doubt_id>/", DoubtReplyView.as_view(), name="doubt_reply"),
]

from django.db import models
from accounts.models import CustomUser, Batch

class SyllabusItem(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='syllabus')
    course_name = models.CharField(max_length=100) # Java, Python, SQL, HTML/CSS/JS
    topic = models.CharField(max_length=200) # e.g. Inheritance, Multi-threading, List Comprehension
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    trainer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'TRAINER'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.batch.name} - {self.course_name} - {self.topic} ({status})"

class Assessment(models.Model):
    syllabus_item = models.OneToOneField(SyllabusItem, on_delete=models.CASCADE, related_name='assessment')
    title = models.CharField(max_length=200)
    questions_json = models.JSONField() # Contains list of 20 MCQs and 1 coding question with solutions
    time_limit_mins = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment for {self.syllabus_item.topic}"

class AssessmentAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='assessment_attempts')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0) # out of 20 for MCQs, coding manually reviewed or automatically checked
    answers_submitted = models.JSONField(blank=True, null=True)
    coding_answer = models.TextField(blank=True, null=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.assessment.syllabus_item.topic} ({self.score}/20)"

class MockRecord(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='mock_records')
    trainer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'TRAINER'}, related_name='trainer_mock_records')
    date = models.DateField()
    
    django_score = models.IntegerField(null=True, blank=True) # out of 100
    python_score = models.IntegerField(null=True, blank=True)
    sql_score = models.IntegerField(null=True, blank=True)
    aptitude_score = models.IntegerField(null=True, blank=True)
    frontend_score = models.IntegerField(null=True, blank=True)
    
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mock for {self.student.username} on {self.date}"

class DoubtMessage(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='student_doubts')
    trainer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'TRAINER'}, related_name='trainer_doubts')
    syllabus_item = models.ForeignKey(SyllabusItem, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Doubt from {self.student.username} to {self.trainer.username}"

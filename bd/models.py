import random
from django.db import models
from accounts.models import CustomUser, Batch

class Job(models.Model):
    ACCEPT_CHOICES = (
        ('MANUAL', 'Manually Accept Applications'),
        ('AUTOMATIC', 'Automatically Shortlist Last-Moment Applications'),
    )

    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField()
    tech_stacks = models.CharField(max_length=200) # e.g. Python, Django, AWS
    salary_package = models.CharField(max_length=100) # e.g. 6.5 LPA
    
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'BD'}, related_name='posted_jobs')
    target_batches = models.ManyToManyField(Batch, related_name='jobs')
    is_open_to_all = models.BooleanField(default=False)
    
    deadline = models.DateTimeField()
    accept_mode = models.CharField(max_length=15, choices=ACCEPT_CHOICES, default='MANUAL')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.company_code:
            # Generate code: DC + company_name first letter + company_name last letter + 3 digit random number
            c_name = self.company_name.strip()
            first_c = c_name[0].upper() if len(c_name) > 0 else 'X'
            last_c = c_name[-1].upper() if len(c_name) > 1 else 'Y'
            rand_num = random.randint(100, 999)
            code = f"DC{first_c}{last_c}{rand_num}"
            while Job.objects.filter(company_code=code).exists():
                rand_num = random.randint(100, 999)
                code = f"DC{first_c}{last_c}{rand_num}"
            self.company_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company_name} ({self.company_code})"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('ROUND_2', 'Cleared Round 2'),
        ('FINAL_ROUND', 'Cleared Final Round'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected'),
    )

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    rejection_reason = models.TextField(blank=True, null=True)
    bd_feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.username} -> {self.job.title} ({self.status})"

class ApplicationTimeline(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='timeline')
    stage = models.CharField(max_length=50) # e.g. "Applied", "Shortlisted", etc.
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.id} stage updated to {self.stage}"

class BDMessage(models.Model):
    DIRECTION_CHOICES = (
        ('BD_TO_STUDENT', 'BD to Student'),
        ('STUDENT_TO_BD', 'Student to BD'),
    )

    bd = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'BD'}, related_name='bd_messages')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'}, related_name='student_bd_messages')
    message = models.TextField()
    file_attachment = models.FileField(upload_to='bd_attachments/', blank=True, null=True)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='BD_TO_STUDENT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.direction} message on {self.created_at}"

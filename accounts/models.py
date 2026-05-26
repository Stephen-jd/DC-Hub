from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('BD', 'Business Development (BD)'),
        ('TRAINER', 'Trainer'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    raw_password_text = models.CharField(max_length=128, blank=True, null=True) # for Admin viewable password

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Batch(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g. PFS008, JFS24
    year = models.IntegerField(default=2026) # e.g. 2026
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

class TrainerBatchLink(models.Model):
    trainer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'TRAINER'}, related_name='trainer_batches')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='batch_trainers')
    technologies = models.CharField(max_length=200) # e.g. Java, Python, SQL
    started_at = models.DateField()

    def __str__(self):
        return f"{self.trainer.username} - {self.batch.name} ({self.technologies})"

class Profile(models.Model):
    DEGREE_CHOICES = (
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('MTECH', 'MTech'),
        ('MSC', 'MSc'),
        ('BSC', 'BSc'),
        ('BE', 'BE'),
        ('BTECH', 'BTech'),
        ('BTECH_CSE', 'BTech CSE'),
        ('BTECH_ECE', 'BTech ECE'),
        ('BTECH_EEE', 'BTech EEE'),
        ('CIVIL', 'Civil'),
        ('OTHER', 'Other Branches'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    phone = models.CharField(max_length=20, blank=True, null=True)
    github_link = models.URLField(max_length=255, blank=True, null=True)
    linkedin_link = models.URLField(max_length=255, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    frontend_skills = models.TextField(blank=True, null=True)
    backend_skills = models.TextField(blank=True, null=True)
    other_skills = models.TextField(blank=True, null=True)
    extra_knowledge = models.TextField(blank=True, null=True) # AI/ML, Cloud, AI, etc.
    
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='BTECH')
    major = models.CharField(max_length=100, blank=True, null=True)
    minor = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

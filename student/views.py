from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.contrib import messages
from django.utils import timezone
from accounts.models import Profile, Batch, TrainerBatchLink, CustomUser
from student.models import SyllabusItem, Assessment, AssessmentAttempt, MockRecord, DoubtMessage
from bd.models import Job, JobApplication, ApplicationTimeline

class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'STUDENT':
            return redirect('dashboard_redirect')
            
        profile = getattr(user, 'profile', None)
        if not profile:
            # Fallback if profile doesn't exist yet
            profile = Profile.objects.create(user=user)
            
        batch = profile.batch
        
        # Calculate Academic Stats
        attempts = AssessmentAttempt.objects.filter(student=user)
        total_attempts = attempts.count()
        avg_assessment_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
        # Convert to percentage (out of 20)
        avg_assessment_pct = round((avg_assessment_score / 20) * 100, 1) if avg_assessment_score else 0

        mock_records = MockRecord.objects.filter(student=user)
        total_mocks = mock_records.count()
        
        # Calculate subject averages
        avg_django = mock_records.filter(django_score__gt=0).aggregate(Avg('django_score'))['django_score__avg'] or 0
        avg_python = mock_records.filter(python_score__gt=0).aggregate(Avg('python_score'))['python_score__avg'] or 0
        avg_sql = mock_records.filter(sql_score__gt=0).aggregate(Avg('sql_score'))['sql_score__avg'] or 0
        avg_aptitude = mock_records.filter(aptitude_score__gt=0).aggregate(Avg('aptitude_score'))['aptitude_score__avg'] or 0
        avg_frontend = mock_records.filter(frontend_score__gt=0).aggregate(Avg('frontend_score'))['frontend_score__avg'] or 0
        
        scores_list = [s for s in [avg_django, avg_python, avg_sql, avg_aptitude, avg_frontend] if s > 0]
        overall_mock_avg = round(sum(scores_list) / len(scores_list), 1) if scores_list else 0

        # Syllabus items
        syllabus_items = SyllabusItem.objects.filter(batch=batch).order_by('completed_date') if batch else []
        completed_syllabus_count = syllabus_items.filter(is_completed=True).count()
        total_syllabus_count = syllabus_items.count()
        syllabus_progress = round((completed_syllabus_count / total_syllabus_count) * 100, 1) if total_syllabus_count else 0
        
        # Placements jobs
        available_jobs = Job.objects.filter(target_batches=batch) | Job.objects.filter(is_open_to_all=True)
        available_jobs = available_jobs.distinct().order_by('-created_at')
        
        applied_jobs = JobApplication.objects.filter(student=user)
        applied_job_ids = applied_jobs.values_list('job_id', flat=True)
        
        # Messages from BD
        from bd.models import BDMessage
        bd_messages = BDMessage.objects.filter(student=user).order_by('-created_at')
        
        # Trainer linked for doubts
        assigned_trainers = []
        if batch:
            assigned_trainers = CustomUser.objects.filter(trainer_batches__batch=batch).distinct()
            
        context = {
            'profile': profile,
            'batch': batch,
            'total_attempts': total_attempts,
            'avg_assessment_pct': avg_assessment_pct,
            'total_mocks': total_mocks,
            'overall_mock_avg': overall_mock_avg,
            'avg_django': round(avg_django, 1),
            'avg_python': round(avg_python, 1),
            'avg_sql': round(avg_sql, 1),
            'avg_aptitude': round(avg_aptitude, 1),
            'avg_frontend': round(avg_frontend, 1),
            'mock_records': mock_records,
            'syllabus_items': syllabus_items,
            'syllabus_progress': syllabus_progress,
            'available_jobs': available_jobs,
            'applied_jobs': applied_jobs,
            'applied_job_ids': list(applied_job_ids),
            'assigned_trainers': assigned_trainers,
            'bd_messages': bd_messages,
            'student_doubts': DoubtMessage.objects.filter(student=user).order_by('-created_at')
        }
        return render(request, 'student/dashboard.html', context)

class StudentExamView(LoginRequiredMixin, View):
    def get(self, request, assessment_id, *args, **kwargs):
        assessment = get_object_or_404(Assessment, id=assessment_id)
        # Check if already attempted
        attempt = AssessmentAttempt.objects.filter(student=request.user, assessment=assessment).first()
        if attempt and attempt.is_completed:
            messages.warning(request, "You have already completed this assessment!")
            return redirect('student_dashboard')
            
        # Get trainer to ask doubt
        trainer = assessment.syllabus_item.trainer or CustomUser.objects.filter(role='TRAINER').first()
        
        context = {
            'assessment': assessment,
            'trainer': trainer,
            'questions': assessment.questions_json[:20],
            'coding_question': assessment.questions_json[20] if len(assessment.questions_json) > 20 else None
        }
        return render(request, 'student/exam.html', context)

    def post(self, request, assessment_id, *args, **kwargs):
        assessment = get_object_or_404(Assessment, id=assessment_id)
        questions = assessment.questions_json[:20]
        
        score = 0
        answers_submitted = {}
        for q in questions:
            q_id = str(q['id'])
            selected_option = request.POST.get(f'q_{q_id}')
            answers_submitted[q_id] = selected_option
            if selected_option == q['answer']:
                score += 1
                
        coding_answer = request.POST.get('coding_answer', '')
        
        AssessmentAttempt.objects.create(
            student=request.user,
            assessment=assessment,
            score=score,
            answers_submitted=answers_submitted,
            coding_answer=coding_answer,
            is_completed=True
        )
        
        messages.success(request, f"Assessment submitted successfully! Score: {score}/20")
        return redirect('student_dashboard')

class StudentProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        profile.github_link = request.POST.get('github_link')
        profile.linkedin_link = request.POST.get('linkedin_link')
        profile.frontend_skills = request.POST.get('frontend_skills')
        profile.backend_skills = request.POST.get('backend_skills')
        profile.other_skills = request.POST.get('other_skills')
        profile.extra_knowledge = request.POST.get('extra_knowledge')
        profile.major = request.POST.get('major')
        profile.minor = request.POST.get('minor')
        
        if 'resume' in request.FILES:
            profile.resume = request.FILES['resume']
            
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('student_dashboard')

class SendDoubtView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        trainer_id = request.POST.get('trainer_id')
        syllabus_item_id = request.POST.get('syllabus_item_id')
        message = request.POST.get('message')
        
        trainer = get_object_or_404(CustomUser, id=trainer_id, role='TRAINER')
        syllabus_item = get_object_or_404(SyllabusItem, id=syllabus_item_id) if syllabus_item_id else None
        
        DoubtMessage.objects.create(
            student=request.user,
            trainer=trainer,
            syllabus_item=syllabus_item,
            message=message
        )
        messages.success(request, "Doubt message sent to trainer!")
        return redirect('student_dashboard')

class ApplyJobView(LoginRequiredMixin, View):
    def post(self, request, job_id, *args, **kwargs):
        job = get_object_or_404(Job, id=job_id)
        
        # Verify student is in target batch or open to all
        student_batch = request.user.profile.batch
        if not job.is_open_to_all and student_batch not in job.target_batches.all():
            messages.error(request, "You are not eligible to apply for this batch-restricted job.")
            return redirect('student_dashboard')
            
        # Check deadline
        if timezone.now() > job.deadline:
            messages.error(request, "Application deadline has passed.")
            return redirect('student_dashboard')
            
        # Create application
        status = 'APPLIED'
        if job.accept_mode == 'AUTOMATIC':
            status = 'SHORTLISTED'
            
        app, created = JobApplication.objects.get_or_create(
            student=request.user,
            job=job,
            defaults={'status': status}
        )
        
        if created:
            ApplicationTimeline.objects.create(
                application=app,
                stage="Applied",
                updated_by=request.user,
                comments="Applied successfully."
            )
            if status == 'SHORTLISTED':
                ApplicationTimeline.objects.create(
                    application=app,
                    stage="Shortlisted",
                    updated_by=CustomUser.objects.filter(role='BD').first(),
                    comments="Auto-shortlisted by system settings."
                )
            messages.success(request, "Applied successfully!")
        else:
            messages.warning(request, "You have already applied for this job.")
            
        return redirect('student_dashboard')

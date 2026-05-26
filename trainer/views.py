from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from accounts.models import Batch, CustomUser, TrainerBatchLink, Profile
from student.models import SyllabusItem, Assessment, MockRecord, DoubtMessage, AssessmentAttempt
from trainer.ai_helper import generate_assessment_via_qwen

class TrainerDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.role != 'TRAINER':
            return redirect('dashboard_redirect')
            
        # Get active batches assigned
        batch_links = TrainerBatchLink.objects.filter(trainer=request.user)
        
        # Get doubt messages
        doubts = DoubtMessage.objects.filter(trainer=request.user).order_by('-created_at')
        
        # Selected batch details for grading/syllabus
        selected_batch_id = request.GET.get('batch_id')
        selected_batch = None
        students = []
        syllabus = []
        
        if selected_batch_id:
            selected_batch = get_object_or_404(Batch, id=selected_batch_id)
            students = CustomUser.objects.filter(role='STUDENT', profile__batch=selected_batch)
            syllabus = SyllabusItem.objects.filter(batch=selected_batch)
        elif batch_links.exists():
            selected_batch = batch_links.first().batch
            students = CustomUser.objects.filter(role='STUDENT', profile__batch=selected_batch)
            syllabus = SyllabusItem.objects.filter(batch=selected_batch)
            
        context = {
            'batch_links': batch_links,
            'selected_batch': selected_batch,
            'students': students,
            'syllabus': syllabus,
            'doubts': doubts,
        }
        return render(request, 'trainer/dashboard.html', context)

class UpdateSyllabusView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(SyllabusItem, id=item_id)
        action = request.POST.get('action') # 'complete' or 'incomplete'
        
        if action == 'complete':
            item.is_completed = True
            item.completed_date = timezone.now().date()
            item.trainer = request.user
            item.save()
            
            # Generate assessment via Qwen AI
            questions = generate_assessment_via_qwen(item.topic)
            
            # Save or update Assessment
            assessment, created = Assessment.objects.update_or_create(
                syllabus_item=item,
                defaults={
                    'title': f"AI Generated Assessment - {item.topic}",
                    'questions_json': questions,
                    'time_limit_mins': 30
                }
            )
            messages.success(request, f"Syllabus updated and Assessment generated automatically for topic: {item.topic}!")
        else:
            item.is_completed = False
            item.completed_date = None
            item.save()
            # Delete associated assessment if desired
            Assessment.objects.filter(syllabus_item=item).delete()
            messages.info(request, "Syllabus topic marked as incomplete.")
            
        return redirect(f"/trainer/dashboard/?batch_id={item.batch.id}")

class MockGraderView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student_id = request.POST.get('student_id')
        batch_id = request.POST.get('batch_id')
        
        student = get_object_or_404(CustomUser, id=student_id, role='STUDENT')
        
        django_score = request.POST.get('django_score') or 0
        python_score = request.POST.get('python_score') or 0
        sql_score = request.POST.get('sql_score') or 0
        aptitude_score = request.POST.get('aptitude_score') or 0
        frontend_score = request.POST.get('frontend_score') or 0
        feedback = request.POST.get('feedback')
        
        MockRecord.objects.create(
            student=student,
            trainer=request.user,
            date=timezone.now().date(),
            django_score=int(django_score),
            python_score=int(python_score),
            sql_score=int(sql_score),
            aptitude_score=int(aptitude_score),
            frontend_score=int(frontend_score),
            feedback=feedback
        )
        
        messages.success(request, f"Mock record updated for {student.username}!")
        return redirect(f"/trainer/dashboard/?batch_id={batch_id}")

class DoubtReplyView(LoginRequiredMixin, View):
    def post(self, request, doubt_id, *args, **kwargs):
        doubt = get_object_or_404(DoubtMessage, id=doubt_id, trainer=request.user)
        reply_text = request.POST.get('reply')
        
        doubt.reply = reply_text
        doubt.replied_at = timezone.now()
        doubt.save()
        
        messages.success(request, "Reply sent successfully!")
        return redirect("/trainer/dashboard/")

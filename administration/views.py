import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Count
from accounts.models import CustomUser, Batch, TrainerBatchLink, Profile
from student.models import MockRecord, AssessmentAttempt

class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return redirect('dashboard_redirect')
            
        # Overall metrics
        total_students = CustomUser.objects.filter(role='STUDENT').count()
        total_batches = Batch.objects.count()
        total_trainers = CustomUser.objects.filter(role='TRAINER').count()
        total_bd = CustomUser.objects.filter(role='BD').count()
        
        # Batch statistics for diagram
        batch_counts = Batch.objects.annotate(student_count=Count('students')).order_by('-year')
        
        # Trainer activities summary (Admin view of mock records summary)
        mock_summary = MockRecord.objects.values('trainer__username', 'date').annotate(count=Count('id')).order_by('-date')[:10]
        
        # Sorting parameters for database
        sort_by = request.GET.get('sort', 'username')
        batch_filter = request.GET.get('batch_id')
        
        student_list = CustomUser.objects.filter(role='STUDENT')
        if batch_filter:
            student_list = student_list.filter(profile__batch_id=batch_filter)
            
        if sort_by == 'name':
            student_list = student_list.order_by('first_name', 'last_name')
        elif sort_by == 'email':
            student_list = student_list.order_by('email')
        elif sort_by == 'mobile':
            student_list = student_list.order_by('profile__phone')
        else:
            student_list = student_list.order_by('username')
            
        context = {
            'total_students': total_students,
            'total_batches': total_batches,
            'total_trainers': total_trainers,
            'total_bd': total_bd,
            'batch_counts': batch_counts,
            'mock_summary': mock_summary,
            'students': student_list[:100], # Paginate for visual performance
            'batches': Batch.objects.all(),
            'trainers': CustomUser.objects.filter(role='TRAINER'),
            'sort_by': sort_by,
            'selected_batch_id': batch_filter
        }
        return render(request, 'administration/dashboard.html', context)

class ManageStudentsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'add':
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            batch_id = request.POST.get('batch')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Create user with a generated clean temp password
            temp_pass = "DCStudent123"
            
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, f"Username {username} already exists!")
                return redirect('admin_dashboard')
                
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=temp_pass,
                role='STUDENT',
                raw_password_text=temp_pass
            )
            
            batch = get_object_or_404(Batch, id=batch_id) if batch_id else None
            Profile.objects.create(
                user=user,
                batch=batch,
                phone=phone
            )
            messages.success(request, f"Student {username} created successfully! Password: {temp_pass}")
            
        elif action == 'edit':
            student_id = request.POST.get('student_id')
            batch_id = request.POST.get('batch')
            
            student = get_object_or_404(CustomUser, id=student_id, role='STUDENT')
            profile = student.profile
            profile.batch = get_object_or_404(Batch, id=batch_id) if batch_id else None
            profile.save()
            messages.success(request, f"Batch updated for {student.username}!")
            
        elif action == 'delete':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(CustomUser, id=student_id, role='STUDENT')
            student.delete()
            messages.error(request, "Student profile deleted successfully.")
            
        return redirect('admin_dashboard')

class ManageBatchesView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        name = request.POST.get('name')
        year = request.POST.get('year', 2026)
        
        if action == 'add':
            if Batch.objects.filter(name=name).exists():
                messages.error(request, f"Batch {name} already exists!")
            else:
                Batch.objects.create(name=name, year=int(year))
                messages.success(request, f"Batch {name} created successfully!")
                
        elif action == 'delete':
            batch_id = request.POST.get('batch_id')
            batch = get_object_or_404(Batch, id=batch_id)
            batch.delete()
            messages.error(request, "Batch deleted successfully.")
            
        return redirect('admin_dashboard')

class AssignTrainerBatchView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        trainer_id = request.POST.get('trainer')
        batch_id = request.POST.get('batch')
        techs = request.POST.get('technologies')
        start_date = request.POST.get('started_at')
        
        trainer = get_object_or_404(CustomUser, id=trainer_id, role='TRAINER')
        batch = get_object_or_404(Batch, id=batch_id)
        
        TrainerBatchLink.objects.create(
            trainer=trainer,
            batch=batch,
            technologies=techs,
            started_at=start_date
        )
        
        messages.success(request, f"Assigned {batch.name} technology ({techs}) to trainer {trainer.username} successfully!")
        return redirect('admin_dashboard')

class ExportStudentsCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_list.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Name', 'Email', 'Phone', 'Batch', 'Year', 'Degree', 'GitHub', 'LinkedIn'])
        
        students = CustomUser.objects.filter(role='STUDENT')
        for s in students:
            prof = getattr(s, 'profile', None)
            writer.writerow([
                s.username,
                f"{s.first_name} {s.last_name}",
                s.email,
                prof.phone if prof else '',
                prof.batch.name if prof and prof.batch else '',
                prof.batch.year if prof and prof.batch else '',
                prof.degree if prof else '',
                prof.github_link if prof else '',
                prof.linkedin_link if prof else ''
            ])
            
        return response

class ImportStudentsCSVView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        batch_name = request.POST.get('batch_name')
        batch_year = request.POST.get('batch_year', 2026)
        
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect('admin_dashboard')
            
        # Parse CSV
        data = csv_file.read().decode('utf-8')
        io_string = io.StringIO(data)
        reader = csv.reader(io_string)
        
        # Skip header
        header = next(reader, None)
        
        # Get or create Batch
        batch, created = Batch.objects.get_or_create(
            name=batch_name,
            defaults={'year': int(batch_year)}
        )
        
        success_count = 0
        for row in reader:
            if not row or len(row) < 3:
                continue
            username = row[0].strip()
            name = row[1].strip()
            email = row[2].strip()
            phone = row[3].strip() if len(row) > 3 else ''
            
            # Avoid duplicate user creation
            if CustomUser.objects.filter(username=username).exists():
                continue
                
            temp_pass = "DCStudent123"
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=name,
                password=temp_pass,
                role='STUDENT',
                raw_password_text=temp_pass
            )
            Profile.objects.create(
                user=user,
                batch=batch,
                phone=phone
            )
            success_count += 1
            
        messages.success(request, f"Imported {success_count} students successfully to batch {batch.name}!")
        return redirect('admin_dashboard')

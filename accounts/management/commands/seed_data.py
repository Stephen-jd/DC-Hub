import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser, Batch, TrainerBatchLink, Profile
from student.models import SyllabusItem, Assessment, AssessmentAttempt, MockRecord, DoubtMessage
from bd.models import Job, JobApplication, ApplicationTimeline

class Command(BaseCommand):
    help = "Seed database with roles (Admin, Trainer, BD, Student) and 500 mock students with statistics"

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing data...")
        CustomUser.objects.all().delete()
        Batch.objects.all().delete()
        SyllabusItem.objects.all().delete()
        Assessment.objects.all().delete()
        AssessmentAttempt.objects.all().delete()
        MockRecord.objects.all().delete()
        Job.objects.all().delete()
        JobApplication.objects.all().delete()
        
        self.stdout.write("Seeding core roles...")
        
        # 1. Admin
        admin_user = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@dclearn.com",
            password="admin",
            role="ADMIN",
            raw_password_text="admin"
        )
        
        # 2. BD
        bd_user = CustomUser.objects.create_user(
            username="naveen",
            email="naveen@dclearn.com",
            password="naveen",
            role="BD",
            raw_password_text="naveen"
        )
        
        # 3. Trainers
        trainer_stephen = CustomUser.objects.create_user(
            username="stephen",
            email="stephen@dclearn.com",
            password="stephen",
            role="TRAINER",
            raw_password_text="stephen"
        )
        trainer_john = CustomUser.objects.create_user(
            username="john",
            email="john@dclearn.com",
            password="john",
            role="TRAINER",
            raw_password_text="john"
        )
        trainer_priya = CustomUser.objects.create_user(
            username="priya",
            email="priya@dclearn.com",
            password="priya",
            role="TRAINER",
            raw_password_text="priya"
        )
        trainer_anjali = CustomUser.objects.create_user(
            username="anjali",
            email="anjali@dclearn.com",
            password="anjali",
            role="TRAINER",
            raw_password_text="anjali"
        )
        
        # Create batches - ONLY PFS008
        pfs008 = Batch.objects.create(name="PFS008", year=2026)
        
        # Link Trainers to Batch
        trainers_list = [
            (trainer_stephen, "Python & Django framework"),
            (trainer_john, "Aptitude"),
            (trainer_priya, "SQL"),
            (trainer_anjali, "Frontend - HTML, CSS, Javascript, React")
        ]
        for tr, techs in trainers_list:
            TrainerBatchLink.objects.create(
                trainer=tr,
                batch=pfs008,
                technologies=techs,
                started_at=timezone.now().date()
            )
        
        # Create Syllabus items and assessments for PFS008
        syllabus_definitions = [
            ("Python", "Python Variables & Loops", trainer_stephen),
            ("Python", "Python Functions & Modules", trainer_stephen),
            ("Django framework", "Django Models & Views", trainer_stephen),
            ("Django framework", "Django Templates & Forms", trainer_stephen),
            ("Aptitude", "Quantitative Aptitude", trainer_john),
            ("Aptitude", "Logical Reasoning & Verbal", trainer_john),
            ("SQL", "SQL DDL & DML Queries", trainer_priya),
            ("SQL", "SQL Joins & Subqueries", trainer_priya),
            ("Frontend - HTML, CSS, Javscript, React", "HTML5 & CSS3 Responsive Layouts", trainer_anjali),
            ("Frontend - HTML, CSS, Javscript, React", "ES6 Javascript & React Components", trainer_anjali)
        ]
        
        syllabus_items = []
        for course, topic, trainer_obj in syllabus_definitions:
            item = SyllabusItem.objects.create(
                batch=pfs008,
                course_name=course,
                topic=topic,
                is_completed=True,
                completed_date=timezone.now().date(),
                trainer=trainer_obj
            )
            syllabus_items.append(item)
            
            # Create Assessment for the topic
            q_json = []
            for i in range(1, 21):
                q_json.append({
                    "id": i,
                    "question": f"Question {i} related to {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A"
                })
            # Add coding question
            q_json.append({
                "type": "coding",
                "question": f"Write a function to implement {topic}.",
                "solution": "def solve():\n    pass"
            })
            
            Assessment.objects.create(
                syllabus_item=item,
                title=f"Assessment - {topic}",
                questions_json=q_json,
                time_limit_mins=30
            )
        
        # 4. Standard Student PFS008 (Vijaykumar)
        student_pfs_user = CustomUser.objects.create_user(
            username="student",
            first_name="Vijaykumar",
            last_name="",
            email="vijaykumar@dclearn.com",
            password="student",
            role="STUDENT",
            raw_password_text="student"
        )
        Profile.objects.create(
            user=student_pfs_user,
            batch=pfs008,
            phone="9876543210",
            github_link="https://github.com/vijaykumar",
            linkedin_link="https://linkedin.com/in/vijaykumar",
            frontend_skills="HTML, CSS, JavaScript",
            backend_skills="Python, Django, SQLite",
            other_skills="Git",
            extra_knowledge="AI/ML",
            degree="BTECH_CSE",
            major="Computer Science",
            minor="Artificial Intelligence"
        )
        
        # Add attempts & mock scores for student
        for item in pfs008.syllabus.all():
            if hasattr(item, 'assessment'):
                AssessmentAttempt.objects.create(
                    student=student_pfs_user,
                    assessment=item.assessment,
                    score=random.randint(14, 20),
                    is_completed=True,
                    answers_submitted={}
                )
        
        MockRecord.objects.create(
            student=student_pfs_user,
            trainer=trainer_stephen,
            date=timezone.now().date(),
            django_score=0,
            python_score=85,
            sql_score=90,
            aptitude_score=88,
            frontend_score=92,
            feedback="Excellent logical thinking and code structure. Communication is clear."
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with only PFS008 and Vijaykumar!"))


from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class LandingPageView(TemplateView):
    template_name = "accounts/landing.html"

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    
    def get_success_url(self):
        return reverse_lazy('dashboard_redirect')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        role = request.user.role
        if role == 'ADMIN':
            return redirect('admin_dashboard')
        elif role == 'BD':
            return redirect('bd_dashboard')
        elif role == 'TRAINER':
            return redirect('trainer_dashboard')
        else:
            return redirect('student_dashboard')

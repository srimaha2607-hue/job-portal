from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from jobs.models import Job, Category, Company
from applications.models import Application, SavedJob
from notifications.models import Notification


@login_required
def index(request):
    user = request.user
    if user.is_admin:
        return redirect('dashboard:admin_dashboard')
    elif user.is_recruiter:
        return redirect('dashboard:recruiter')
    else:
        return redirect('dashboard:seeker')


@login_required
def seeker_dashboard(request):
    user = request.user
    applications = Application.objects.filter(applicant=user).select_related('job', 'job__company')
    saved = SavedJob.objects.filter(user=user).count()
    stats = {
        'total_applied': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
        'saved_jobs': saved,
    }
    recent_apps = applications[:5]
    recent_notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    return render(request, 'dashboard/seeker.html', {
        'stats': stats,
        'recent_applications': recent_apps,
        'recent_notifications': recent_notifications,
    })


@login_required
def recruiter_dashboard(request):
    if not (request.user.is_recruiter or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:seeker')
    user = request.user
    jobs = Job.objects.filter(poster=user).prefetch_related('applications')
    total_jobs = jobs.count()
    total_applications = Application.objects.filter(job__poster=user).count()
    pending = Application.objects.filter(job__poster=user, status='pending').count()
    accepted = Application.objects.filter(job__poster=user, status='accepted').count()
    recent_applications = Application.objects.filter(job__poster=user).select_related('applicant', 'job').order_by('-applied_at')[:10]
    job_stats = jobs.annotate(app_count=Count('applications')).order_by('-app_count')[:5]
    return render(request, 'dashboard/recruiter.html', {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending': pending,
        'accepted': accepted,
        'recent_applications': recent_applications,
        'job_stats': job_stats,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'Admin access only.')
        return redirect('dashboard:index')
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    stats = {
        'total_users': User.objects.count(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'total_applications': Application.objects.count(),
        'total_companies': Company.objects.count(),
        'new_users_month': User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'new_jobs_month': Job.objects.filter(created_at__gte=thirty_days_ago).count(),
        'seekers': User.objects.filter(role='seeker').count(),
        'recruiters': User.objects.filter(role='recruiter').count(),
    }
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_jobs = Job.objects.order_by('-created_at').select_related('poster', 'company')[:5]
    recent_apps = Application.objects.order_by('-applied_at').select_related('applicant', 'job')[:5]
    categories_data = Category.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:6]
    return render(request, 'dashboard/admin.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_apps,
        'categories_data': categories_data,
    })

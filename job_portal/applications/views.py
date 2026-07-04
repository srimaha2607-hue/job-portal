from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from jobs.models import Job
from .models import Application, SavedJob
from .forms import ApplicationForm
from notifications.models import Notification


@login_required
def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', slug=slug)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            if not app.resume:
                try:
                    app.resume = request.user.profile.resume
                except Exception:
                    pass
            app.save()
            Notification.objects.create(
                user=request.user,
                title='Application Submitted',
                message=f'Your application for "{job.title}" has been submitted.',
                notification_type='applied'
            )
            if job.poster:
                Notification.objects.create(
                    user=job.poster,
                    title='New Application',
                    message=f'{request.user.full_name} applied for "{job.title}".',
                    notification_type='new_application'
                )
            messages.success(request, 'Application submitted successfully!')
            return redirect('applications:applied_jobs')
    else:
        form = ApplicationForm()
    return render(request, 'applications/apply_job.html', {'form': form, 'job': job})


@login_required
def applied_jobs(request):
    apps = Application.objects.filter(applicant=request.user).select_related('job', 'job__company')
    paginator = Paginator(apps, settings.APPLICATIONS_PER_PAGE)
    page = request.GET.get('page')
    return render(request, 'applications/applied_jobs.html', {'applications': paginator.get_page(page)})


@login_required
def saved_jobs(request):
    saved = SavedJob.objects.filter(user=request.user).select_related('job', 'job__company')
    return render(request, 'applications/saved_jobs.html', {'saved_jobs': saved})


@login_required
def toggle_save_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        saved_status = False
    else:
        saved_status = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved_status})
    return redirect('jobs:job_detail', slug=slug)


@login_required
def application_detail(request, pk):
    app = get_object_or_404(Application, pk=pk, applicant=request.user)
    return render(request, 'applications/application_detail.html', {'application': app})


@login_required
def update_application_status(request, pk):
    app = get_object_or_404(Application, pk=pk)
    if request.user != app.job.poster and not request.user.is_admin:
        messages.error(request, 'Not authorized.')
        return redirect('dashboard:recruiter')
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('recruiter_notes', '')
        if status in dict(Application.STATUS_CHOICES):
            app.status = status
            app.recruiter_notes = notes
            app.save()
            notif_type = 'accepted' if status == 'accepted' else 'rejected' if status == 'rejected' else 'reviewed'
            Notification.objects.create(
                user=app.applicant,
                title=f'Application {status.title()}',
                message=f'Your application for "{app.job.title}" has been {status}.',
                notification_type=notif_type
            )
            messages.success(request, f'Application marked as {status}.')
    return redirect('dashboard:recruiter')

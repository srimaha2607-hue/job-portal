from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from .models import Job, Category, Company
from .forms import JobForm, JobSearchForm, CompanyForm
from applications.models import Application, SavedJob


def home(request):
    featured_jobs = Job.objects.filter(is_active=True, is_featured=True).select_related('company', 'category')[:6]
    recent_jobs = Job.objects.filter(is_active=True).select_related('company', 'category')[:8]
    categories = Category.objects.all()[:8]
    total_jobs = Job.objects.filter(is_active=True).count()
    total_companies = Company.objects.count()
    return render(request, 'jobs/home.html', {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'categories': categories,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    })


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('company', 'category', 'poster')
    form = JobSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')
        experience_level = form.cleaned_data.get('experience_level')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        if q:
            jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(skills_required__icontains=q))
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        if salary_min:
            jobs = jobs.filter(salary_min__gte=salary_min)
        if salary_max:
            jobs = jobs.filter(salary_max__lte=salary_max)
    paginator = Paginator(jobs, settings.JOBS_PER_PAGE)
    page = request.GET.get('page')
    jobs_page = paginator.get_page(page)
    return render(request, 'jobs/job_list.html', {'jobs': jobs_page, 'form': form, 'total': jobs.count()})


def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    job.views_count += 1
    job.save(update_fields=['views_count'])
    similar_jobs = Job.objects.filter(category=job.category, is_active=True).exclude(pk=job.pk)[:4]
    has_applied = False
    is_saved = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()
    return render(request, 'jobs/job_detail.html', {
        'job': job, 'similar_jobs': similar_jobs,
        'has_applied': has_applied, 'is_saved': is_saved,
    })


@login_required
def create_job(request):
    if not (request.user.is_recruiter or request.user.is_admin):
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('jobs:home')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', slug=job.slug)
    else:
        form = JobForm()
        form.fields['company'].queryset = Company.objects.filter(owner=request.user)
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Post New Job'})


@login_required
def edit_job(request, slug):
    job = get_object_or_404(Job, slug=slug, poster=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:job_detail', slug=job.slug)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@login_required
def delete_job(request, slug):
    job = get_object_or_404(Job, slug=slug, poster=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted.')
        return redirect('dashboard:recruiter')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})

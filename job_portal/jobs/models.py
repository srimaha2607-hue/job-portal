from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='briefcase')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Company(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    size = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def logo_url(self):
        if self.logo:
            return self.logo.url
        return '/static/images/default-company.png'


class Job(models.Model):
    TYPE_FULL_TIME = 'full_time'
    TYPE_PART_TIME = 'part_time'
    TYPE_CONTRACT = 'contract'
    TYPE_INTERNSHIP = 'internship'
    TYPE_FREELANCE = 'freelance'
    TYPE_REMOTE = 'remote'
    JOB_TYPES = [
        (TYPE_FULL_TIME, 'Full Time'),
        (TYPE_PART_TIME, 'Part Time'),
        (TYPE_CONTRACT, 'Contract'),
        (TYPE_INTERNSHIP, 'Internship'),
        (TYPE_FREELANCE, 'Freelance'),
        (TYPE_REMOTE, 'Remote'),
    ]

    EXP_ENTRY = 'entry'
    EXP_MID = 'mid'
    EXP_SENIOR = 'senior'
    EXP_LEAD = 'lead'
    EXP_CHOICES = [
        (EXP_ENTRY, 'Entry Level (0-2 years)'),
        (EXP_MID, 'Mid Level (2-5 years)'),
        (EXP_SENIOR, 'Senior Level (5-10 years)'),
        (EXP_LEAD, 'Lead / Manager (10+ years)'),
    ]

    poster = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    skills_required = models.CharField(max_length=500, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default=TYPE_FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=EXP_CHOICES, default=EXP_MID)
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='USD')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f'{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}'
        if self.salary_min:
            return f'{self.salary_currency} {self.salary_min:,}+'
        return 'Negotiable'

    @property
    def company_name(self):
        return self.company.name if self.company else 'Confidential'

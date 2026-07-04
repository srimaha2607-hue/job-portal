from django.contrib import admin
from .models import Job, Category, Company


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'location', 'industry']
    search_fields = ['name', 'owner__email']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'poster', 'company', 'job_type', 'is_active', 'is_featured', 'created_at']
    list_filter = ['job_type', 'is_active', 'is_featured', 'experience_level']
    search_fields = ['title', 'poster__email', 'location']
    prepopulated_fields = {'slug': ('title',)}

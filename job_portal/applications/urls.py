from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<slug:slug>/', views.apply_job, name='apply_job'),
    path('applied/', views.applied_jobs, name='applied_jobs'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    path('save/<slug:slug>/', views.toggle_save_job, name='toggle_save'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/status/', views.update_application_status, name='update_status'),
]

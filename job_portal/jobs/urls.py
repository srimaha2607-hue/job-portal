from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<slug:slug>/', views.job_detail, name='job_detail'),
    path('jobs/<slug:slug>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<slug:slug>/delete/', views.delete_job, name='delete_job'),
]

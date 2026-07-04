from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('seeker/', views.seeker_dashboard, name='seeker'),
    path('recruiter/', views.recruiter_dashboard, name='recruiter'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]

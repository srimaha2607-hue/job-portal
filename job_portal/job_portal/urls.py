from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from job_portal.views import error_403, error_404, error_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('accounts/', include('accounts.urls')),
    path('applications/', include('applications.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('faq/', TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = error_403
handler404 = error_404
handler500 = error_500

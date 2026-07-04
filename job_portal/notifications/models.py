from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('applied', 'Job Applied'),
        ('accepted', 'Application Accepted'),
        ('rejected', 'Application Rejected'),
        ('reviewed', 'Application Reviewed'),
        ('new_application', 'New Application'),
        ('new_job', 'New Job Posted'),
        ('password_changed', 'Password Changed'),
        ('general', 'General'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.title}'

from .models import Notification


def notifications_processor(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        recent = Notification.objects.filter(user=request.user)[:5]
        return {'unread_notifications': unread, 'recent_notifications': recent}
    return {'unread_notifications': 0, 'recent_notifications': []}

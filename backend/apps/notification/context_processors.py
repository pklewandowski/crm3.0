from apps.notification.models import NotificationUser
from apps.user.models import User


def get_notifications(request):
    notifications = None
    if request.user and isinstance(request.user, User):
        notifications = [i.notification for i in NotificationUser.objects.filter(user=request.user).exclude(status='CL').order_by('-notification__effective_date')]  # context_data

    return {'notifications': notifications}

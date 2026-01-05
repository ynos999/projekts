from django.shortcuts import redirect
from django.views.generic import ListView, View
from django.http import JsonResponse
from .models import Notification

class MarkNotificationAsRead(View):
    def post(self, request, notification_id):
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()
        return redirect("notifications:notification-list")

class NotificationListView(ListView):
    model = Notification
    context_object_name = "notifications"
    template_name = "notifications/notification_list.html"
    paginate_by = 5

    def get_queryset(self):
        return self.request.user.notifications.all().select_related('actor__profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_notifications = self.request.user.notifications.unread(self.request.user)            
        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        return context

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(read=False).count()
        return JsonResponse({'unread_count': count})
    return JsonResponse({'unread_count': 0})
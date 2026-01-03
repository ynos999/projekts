from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from .models import Notification
from django.http import JsonResponse

# Create your views here.

class MarkNotificationAsRead(View):
    def post(self, request, notification_id):
        # get notification
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()

        return redirect("notifications:notification-list")


class NotificationListView(ListView):
    model = Notification
    context_object_name = "notifications"
    template_name = "notifications/notification_list.html"
    paginate_by = 5

    def get_queryset(self):
        # return self.request.user.notifications.unread(self.request.user)
        # return self.request.user.notifications.filter(read=False).select_related('actor__profile')
        return self.request.user.notifications.all().select_related('actor__profile')
        

    def get_context_data(self, **kwargs):
        # latest notifications
        context = super(NotificationListView, self).get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread(self.request.user)            
        
        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        context["header_text"] = "Notifications"
        context["title"] = "All All Notifications"
        return context
    
    
    # notifications/tasks.py

def create_notification(actor_username, verb, object_id, content_type_model, content_type_app_label):
    try:
        actor = User.objects.get(username=actor_username)
        content_type = ContentType.objects.get(model=content_type_model, app_label=content_type_app_label)
        content_object = content_type.get_object_for_this_type(id=object_id)

        recipients = []
        
        # Noteikšana saņēmējam
        if content_type_model == "task":
            # Pārbaudi, vai Tavā Task modelī lauks tiešām ir 'user_assigned_to'
            # Ja tas ir 'assigned_to', nomaini šeit!
            if hasattr(content_object, "user_assigned_to") and content_object.user_assigned_to:
                recipients = [content_object.user_assigned_to]
            elif hasattr(content_object, "assigned_to") and content_object.assigned_to:
                recipients = [content_object.assigned_to]
        
        elif content_type_model == "project":
            if hasattr(content_object, "team") and content_object.team:
                recipients = content_object.team.members.all()

        for recipient in recipients:
            Notification.objects.create(
                receipient=recipient, # Pārbaudi šo burtu secību modelī!
                actor=actor,
                verb=verb,
                content_type=content_type,
                content_object=content_object,
                read=False
            )
        return True
    except Exception as e:
        print(f"Paziņojuma kļūda: {e}")
        return False
    

def unread_notifications_count(request):
    if request.user.is_authenticated:
        # Izmantojam Tavu NotificationManager vai vienkāršu filtru
        count = request.user.notifications.filter(read=False).count()
        return JsonResponse({'unread_count': count})
    return JsonResponse({'unread_count': 0})
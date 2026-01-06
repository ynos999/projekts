# notifications/tasks.py
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Notification

@shared_task
def create_notification(actor_username, verb, object_id, content_type_model, content_type_app_label):
    try:
        actor = User.objects.get(username=actor_username)
        content_type = ContentType.objects.get(model=content_type_model, app_label=content_type_app_label)
        content_object = content_type.get_object_for_this_type(id=object_id)

        recipients = []
        project = None

        if content_type_model == "task":
            project = getattr(content_object, 'project', None)
            # Izmantojam Tavu pareizo lauku
            assigned_user = getattr(content_object, 'user_assigned_to', None)
            if assigned_user:
                recipients = [assigned_user]
            elif hasattr(content_object, "owner"):
                recipients = [content_object.owner]
        
        # notifications/tasks.py fragmentā:
        elif content_type_model == "project":
            project = content_object
            # Pievienojam visus komandas biedrus
            if hasattr(content_object, "team") and content_object.team:
                recipients = list(content_object.team.members.all())
            
            # Pievienojam arī pašu īpašnieku, ja viņš nav komandā vai grib saņemt kopiju
            if content_object.owner not in recipients:
                recipients.append(content_object.owner)

        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                actor=actor,
                verb=verb,
                content_type=content_type,
                content_object=content_object,
                read=False
            )
            if recipient.email:
                send_html_notification_email(recipient, verb, project)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_html_notification_email(recipient, verb, project):
    # Šeit ir Tava izvēlētā subjekta līnija
    subject = f" {verb}"
    
    context = {
        'username': recipient.username,
        'verb': verb,
        'project': project,
        'base_url': 'http://127.0.0.1:8000'
    }
    
    html_content = render_to_string('emails/notification_email.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient.email]
    )
    email.content_subtype = "html"
    email.send(fail_silently=True)
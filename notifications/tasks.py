from celery import shared_task
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .models import Notification
from projects.models import Project

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


@shared_task
def create_notification(actor_username, verb, object_id, content_type_model, content_type_app_label):
    try:
        actor = User.objects.get(username=actor_username)
        content_type = ContentType.objects.get(model=content_type_model, app_label=content_type_app_label)
        content_object = content_type.get_object_for_this_type(id=object_id)

        recipients = []
        project = None

        # Nosakām saņēmējus un mēģinām atrast saistīto projektu e-pasta kontekstam
        if content_type_model == "project":
            project = content_object
            if hasattr(content_object, "team") and content_object.team:
                recipients = content_object.team.members.all()
        
        elif content_type_model == "task":
            project = getattr(content_object, 'project', None)
            if hasattr(content_object, "assigned_to") and content_object.assigned_to:
                recipients = [content_object.assigned_to]
            elif hasattr(content_object, "owner"):
                recipients = [content_object.owner]

        notification_ids = []
        for recipient in recipients:
            # 1. Izveidojam ierakstu datubāzē
            notification = Notification.objects.create(
                receipient=recipient,
                actor=actor,
                verb=verb,
                content_type=content_type,
                content_object=content_object,
                read=False
            )
            notification_ids.append(notification.id)

            # 2. Nosūtām HTML e-pastu
            if recipient.email:
                send_html_notification_email(recipient, verb, project)

        return notification_ids
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None

def send_html_notification_email(recipient, verb, project):
    """Palīgfunkcija HTML e-pasta sūtīšanai"""
    subject = f"Swifthub paziņojums"
    
    # Sagatavojam datus veidnei
    context = {
        'username': recipient.username,
        'verb': verb,
        'project': project,
        'base_url': 'http://127.0.0.1:8000' # Vēlāk šeit būs Tavs domēns
    }
    
    # Renderējam HTML saturu no faila
    html_content = render_to_string('emails/notification_email.html', context)
    
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient.email]
    )
    email.content_subtype = "html"
    email.send(fail_silently=True)


# def create_notification(actor_username, verb, object_id, content_type_model, content_type_app_label):
#     try:
#         actor = User.objects.get(username=actor_username)
#         content_type = ContentType.objects.get(model=content_type_model, app_label=content_type_app_label)
#         content_object = content_type.get_object_for_this_type(id=object_id)

#         recipients = []
        
#         # 1. Ja tas ir Projekts (meklējam komandu)
#         if content_type_model == "project":
#             if hasattr(content_object, "team") and content_object.team:
#                 recipients = content_object.team.members.all()
        
#         # 2. Ja tas ir Uzdevums (meklējam konkrētu lietotāju)
#         elif content_type_model == "task":
#             # Pārliecinies, ka lauks ir 'assigned_to' vai 'owner'
#             if hasattr(content_object, "assigned_to") and content_object.assigned_to:
#                 recipients = [content_object.assigned_to]
#             elif hasattr(content_object, "owner"):
#                 recipients = [content_object.owner]

#         notification_ids = []
#         for recipient in recipients:
#             # Neveidojam paziņojumu, ja aktors un saņēmējs ir tas pats cilvēks
#             # if recipient == actor: continue 

#             notification = Notification.objects.create(
#                 receipient=recipient, # Pārliecinies, vai modelī nav drukas kļūda 'receipient' vs 'recipient'
#                 actor=actor,
#                 verb=verb,
#                 content_type=content_type,
#                 content_object=content_object,
#                 read=False
#             )
#             notification_ids.append(notification.id)

#         return notification_ids
#     except Exception as e:
#         print(f"Error creating notification: {e}")
#         return None

@shared_task
def notify_teams_due_projects_tasks():
    project_due_soon = Project.objects.due_in_two_days_or_less()

    for project in project_due_soon:
        verb = f"Reminder: The project {project.name} is due soon!"
        actor_username = project.owner.username

        members = project.team.members.all()
        for member in members:
            create_notification.delay(
                actor_username=actor_username,
                verb=verb,
                object_id=project.id,
                content_type_model = "project",
                content_type_app_label = "projects"
            )


# Pārliecinies, ka šī funkcija ir pieejama
def send_notification_email(user, subject, message):
    if user.email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False, # Testēšanas laikā labāk False, lai redzi kļūdas terminālī
        )
        
def send_html_email(user, project, verb):
    # Pārbaudām vai lietotājam ir e-pasts
    if not user.email:
        return
        
    context = {
        'user': user,
        'project': project,
        'verb': verb,
        'domain': '127.0.0.1:8000' # Vēlāk nomaini uz īsto domēnu
    }
    
    # Šeit mēs norādām ceļu uz HTML failu, ko tūlīt izveidosim
    html_content = render_to_string('emails/notification_email.html', context)
    
    email = EmailMessage(
        subject=f"Swifthub: {verb[:50]}...",
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.content_subtype = "html" # Svarīgi, lai sūtītu kā HTML
    email.send(fail_silently=True)
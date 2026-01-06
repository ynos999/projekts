from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from projects.models import Project

STATUS_CHOICES = [
    ('Backlog', 'Backlog'),
    ('To Do', 'To Do'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
]


PRIORITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
]


class TaskQueryset(models.QuerySet):
    def active(self):
        return self.filter(active=True)
    
    def upcoming(self):
        return self.filter(
            models.Q(due_date__gte=timezone.now()) | models.Q(due_date__isnull=True))
    
    def for_user(self, user):
        return self.filter(models.Q(owner=user) | models.Q(project__team__members=user)).distinct()
    

class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQueryset(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().active().upcoming()
    
    def for_user(self, user):
        return self.get_queryset().active().upcoming().for_user(user)



class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    user_assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        null=True,
        blank=True
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Backlog", db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="Medium", db_index=True)
    start_date = models.DateField(null=True, blank=True, db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = TaskManager()


    def __str__(self):
        return self.name

        
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Paātrina filtrēšanu Kanban dēlim un pārskatiem
            models.Index(fields=['status', 'priority']),
            # Paātrina noklusējuma kārtošanu (ordering)
            models.Index(fields=['-created_at']),
            # Paātrina uzdevumu atlasi konkrēta projekta ietvaros
            models.Index(fields=['project', 'status']),
            # Papildus: Ja bieži meklē pēc izpildes termiņa
            models.Index(fields=['due_date']),
        ]

    
    def days_until_due(self):
        if self.due_date:
            #get current date
            current_date = timezone.now().date()
            return (self.due_date - current_date).days
        return None
    
    @property
    def progress(self):
        progress_dict ={
            'To Do': 0,
            'In Progress': 50,
            'Completed': 100,
        }
        return progress_dict.get(self.status, 0)
    

    @property
    def status_color(self):
        status_value = self.progress
        if status_value == 100:
            color = "success"
        elif status_value == 50:
            color = "primary"
        else:
            color = ""
        return color

    def priority_color(self):
        if self.priority == "Low":
            color = "success"
        elif self.priority == "Medium":
            color = "warning"
        else:
            color = "danger"
        return color
    

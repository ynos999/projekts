from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
  
class NotificationManager(models.Manager):
    def unread(self, user):
        # Filtrējam paziņojumus, kur saņēmējs ir konkrētais lietotājs un tie nav izlasīti
        return self.filter(recipient=user, read=False)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    verb = models.CharField(max_length=255)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False, db_index=True) # Pievienojam index šeit

    objects = NotificationManager()

    def __str__(self):
        return f'{self.actor} {self.verb} {self.content_object}'
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # SVARĪGI: Lauku nosaukumiem jāsakrīt ar augstāk definētajiem (recipient, read)
            models.Index(fields=['recipient', 'read']),
            models.Index(fields=['-created_at']),
        ]

    @property
    def notification_time_formatted(self):
        return self.created_at.strftime('%d %b %I %M %p')

    def mark_as_read(self):
        self.read = True
        self.save()

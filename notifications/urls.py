from django.urls import path
from .views import NotificationListView, MarkNotificationAsRead
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name="notification-list"),
    path('<int:notification_id>/read/', MarkNotificationAsRead.as_view(), name="mark_as_read"),
    path('unread-count/', views.unread_notifications_count, name='unread-count'),
]

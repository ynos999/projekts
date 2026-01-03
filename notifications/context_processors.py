def notification_context(request):
    if request.user.is_authenticated:
        # Iegūstam neizlasītos paziņojumus pašreizējam lietotājam
        unread_notifications = request.user.notifications.unread(request.user)
        return {
            'latest_notifications': unread_notifications.order_by('-created_at')[:5],
            'notification_count': unread_notifications.count()
        }
    return {
        'latest_notifications': [],
        'notification_count': 0
    }
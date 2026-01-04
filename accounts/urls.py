from django.urls import path
from .views import (
    DashboardView,
    MembersListView,
    RegisterView,
    ProfileDetailView,
    PasswordChangeView,
    ProfileUpdateView
)

from . import views
from .forms import LoginFormWithCaptcha
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import MyLoginView
from accounts.views import MyLoginView

app_name = 'accounts'

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('members/', MembersListView.as_view(), name="members-list"),
    path('<int:pk>/user/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/edit/', ProfileUpdateView.as_view(), name='profile-update'),
    path('search/', views.global_search, name='global-search'),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
    
    # Tikai viena rinda pieteikšanās procesam!
    path('login/', MyLoginView.as_view(), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
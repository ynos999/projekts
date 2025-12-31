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

app_name = 'accounts'

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('members', MembersListView.as_view(), name="members-list"),
    # path('register/', RegisterView, name='register'),
    path('<int:pk>/user/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/edit/', ProfileUpdateView.as_view(), name='profile-update'),
    
    path('search/', views.global_search, name='global-search'),
    

    # change password
    path('password-change', PasswordChangeView.as_view(), name='password-change'),
    
    # PIEVIENO ŠOS DIVUS:

    path('logout/', auth_views.LogoutView.as_view(
        next_page='accounts:login' # Pēc iziešanas metīs uz login
    ), name='logout'),
    
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=LoginFormWithCaptcha # Tagad šis strādās
    ), name='login'),
]

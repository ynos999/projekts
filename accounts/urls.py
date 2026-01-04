from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Importējam visu moduli, lai novērstu ciklus

app_name = 'accounts'

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('members/', views.MembersListView.as_view(), name="members-list"),
    path('<int:pk>/user/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/edit/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('search/', views.global_search, name='global-search'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # ŠĪ RINDIŅA IR SVARĪGĀKĀ:
    path('login/', views.MyLoginView.as_view(), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
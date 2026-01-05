from django.contrib import admin
from .models import Profile
from .forms import LoginFormWithCaptcha

admin.site.register(Profile)

# Šī rinda liek Django Admin panelim izmantot tavu formu ar Captcha
admin.site.login_form = LoginFormWithCaptcha
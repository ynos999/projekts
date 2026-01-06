# ** A Django-Based Project Management System**

- **Frontend**: HTML, CSS, JavaScript, AdminLTE3
**Project Management** is a robust and flexible project management system built using Django and AdminLTE3. It is designed to enhance team collaboration, streamline task tracking, and simplify project progress monitoring. With its modern interface and rich features, **Project Management** caters to organizations, teams, and individuals aiming for efficient project workflows.

---

## **Table of Contents**
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Installation](#installation)
4. [Usage](#usage)

---

## **Features**
- **Kanban Board**: Drag-and-drop interface for task management.
- **Notifications**: Real-time alerts for task deadlines and updates.
- **Progress Tracking**: Automatic calculation of project progress.
- **Team Collaboration**: Assign roles and manage permissions.
- **Access Levels**: Role-based access control for users.
- **Attachments & Comments**: Upload files and communicate within tasks.
- **AdminLTE3 Integration**: Responsive and user-friendly UI design.
- **Task Deadline Alerts**: Notifications for tasks nearing expiry.
- **Customizable Templates**: Easily modify layout and design.

---

## **Technologies Used**
- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript, AdminLTE3
- **Database**: SQLite (default), with support for PostgreSQL and MySQL
- **Task Queue**: Celery
- **Notification System**: Redis

---

## **Installation**

### **Prerequisites**
- Python 3.9+
- pip (Python package manager)
- Virtual environment (recommended)

---
# If use localy:

   ```
0. Copy Repo.
   ```

1. Creating virtual environment and activating it linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply Migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create Super User:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the Server:
   ```bash
   python manage.py runserver


   export DJANGO_DB=sqlite
   python manage.py runserver
   ```

First create .env file. Rename .backup_env to .env:

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,mydomain.com,*

RECAPTCHA_PUBLIC_KEY = 'YourKeyHere'
RECAPTCHA_PRIVATE_KEY = 'YourKeyHere'

SECRET_KEY = 'SecureKey'

# Database configuration
DB_USER=
DB_PASS=
DB_NAME=
DB_HOST=
DB_PORT=

REDIS_HOST=redis
REDIS_PORT=6379

# EMAIL CREDENTIALS
EMAIL_HOST=
EMAIL_USE_TLS=True
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=YourPasswordHere
DEFAULT_FROM_EMAIL=
EMAIL_USE_SSL=False

### **Project Structure**

# For dumpdata:
```bash
python manage.py shell
# Inside shell:
from django.apps import apps
print([app.label for app in apps.get_app_configs()])

['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'tempus_dominus', 'crispy_forms', 'crispy_bootstrap5', 'django_celery_beat', 'phonenumber_field', 'accounts', 'projects', 'tasks', 'notifications', 'teams', 'comments']
```

# Create fixturas:
```bash
python manage.py dumpdata auth.group auth.user projects teams tasks comments \
--indent 2 \
--natural-foreign \
--natural-primary \
--exclude auth.permission \
--exclude contenttypes \
--exclude accounts.profile \
--exclude notifications \
-o fixturas.json

python manage.py shell -c "from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
```

# Load fixturas.json:
```bash
python manage.py loaddata fixturas.json
```

# IF You use docker-compose localy:
```bash
docker compose down
docker compose down -v
docker compose build --no-cache
docker compose up
```
# If You use github worklows add secrets:
```
          ALLOWED_HOSTS: ${{ secrets.ALLOWED_HOSTS }}
          RECAPTCHA_PUBLIC_KEY: ${{ secrets.RECAPTCHA_PUBLIC_KEY }}
          RECAPTCHA_PRIVATE_KEY: ${{ secrets.RECAPTCHA_PRIVATE_KEY }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASS: ${{ secrets.DB_PASS }}
          DB_NAME: ${{ secrets.DB_NAME }}
          DB_HOST: ${{ secrets.DB_HOST }}
          EMAIL_HOST: ${{ secrets.EMAIL_HOST }}
          EMAIL_HOST_USER: ${{ secrets.EMAIL_HOST_USER }}
          EMAIL_HOST_PASSWORD: ${{ secrets.EMAIL_HOST_PASSWORD }}
          DEFAULT_FROM_EMAIL: ${{ secrets.EMAIL_HOST_USER }}
          TEST_TUNNEL_TOKEN: ${{ secrets.TUNNEL_TOKEN }}
          HOSTS: ${{ secrets.ALLOWED_HOSTS }}
          FIXTURES_DATA: ${{ secrets.FIXTURES_DATA }}
```

# Test
```bash
docker exec projekti-web python manage.py shell -c "from django.conf import settings; print(f'DEBUG: {settings.DEBUG}'); print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}'); print(f'CSRF_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}')"
docker exec projekti-web python manage.py check
docker exec projekti-web python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"
docker exec projekti-web ls -l /usr/src/app/
```

# Fixturas from docker:
```bash
docker exec -it projekti-web /bin/bash
# or root
docker exec -u 0 -it projekti-web /bin/bash
python manage.py dumpdata auth.user accounts projects teams tasks notifications comments --indent 4 -o fixturas.json
docker cp projekti-web:/usr/src/app/fixturas.json /home/wolf
```

# Raed celery_worker_err.log
```bash
docker exec -it projekti-web tail -f /tmp/celery_worker_err.log
```
# Show emails env
```bash
docker exec -it projekti-web python manage.py shell -c "from django.conf import settings; print(f'HOST: {settings.EMAIL_HOST}, PORT: {settings.EMAIL_PORT}, TLS: {settings.EMAIL_USE_TLS}, USER: {settings.EMAIL_HOST_USER}')"

docker exec -it projekti-web python manage.py shell -c "from django.conf import settings; print(f'TLS status: {settings.EMAIL_USE_TLS}')"
```

```bash
docker exec -it projekti-web python manage.py shell -c "from django.core.mail import send_mail; send_mail('Testa epasts', 'Sveiki bez izsauksuma zimes', 'sender@gmail.com', ['receiver@gmail.com'], fail_silently=False)"
```

# Python shell.
```bash
python manage.py shell
```

# Delete notifications
```bash
from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM notifications_notification;")
connection.commit()
exit()
```
# Makemigrations
```bash
python manage.py makemigrations
python manage.py migrate
```

# Delete all dokers from server.
```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
docker volume prune -f
docker system prune -a --volumes
```


# Read logs
```bash
docker logs projekti-web
docker logs projekti-postgresdb
```
# 1. Izveido tabulu struktūru (šoreiz bez kļūdām par 'recipient_id')
docker exec -it projekti-web python manage.py migrate
# 2. Savāc statiskos failus (lai nav 404/500 kļūdu CSS failiem)
docker exec -it projekti-web python manage.py collectstatic --noinput
# 3. Ielādē sākuma datus

docker exec -it projekti-web python manage.py loaddata fixturas.json

# 1. Apturēt visus projekta konteinerus
docker ps -q | xargs -r docker stop
docker stop $(docker ps -q)
# 2. Izdzēst visus konteinerus
docker ps -aq | xargs -r docker rm
# 3. IZDZĒST VISUS VOLUMES (Šis izdzēsīs veco Postgres datus ar kļūdaino recipient_id)
docker volume prune -f
# 4. Drošībai izdzēst vecos image, lai GitHub Workflow būvē visu no jauna
docker image prune -a -f
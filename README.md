# ** A Django-Based Project Management System**

- **Frontend**: HTML, CSS, JavaScript, AdminLTE3
**Project Management** is a robust and flexible project management system built using Django and AdminLTE3. It is designed to enhance team collaboration, streamline task tracking, and simplify project progress monitoring. With its modern interface and rich features, **Project Management** caters to organizations, teams, and individuals aiming for efficient project workflows.

---

## **Table of Contents**
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Installation](#installation)
4. [Usage](#usage)
5. [env] (#env)

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
- **Send to mail**:

---

## **Technologies Used**
- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript, AdminLTE3
- **Database**: SQLite (default), with support for PostgreSQL and MySQL
- **Task Queue**: Celery
- **Notification System**: Redis
- **SMTP**: Mail server
- **Capcha**: Google recapcha v3
- **Hetzner**: Terraform
- **Github**: Workflows

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
---

## **env**
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

# docker exec -it projekti-web python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 > ~/all_dump.json

# docker exec -it projekti-web python manage.py dumpdata auth.user auth.group --natural-foreign --indent 2 > ~/users_groups.json

# docker exec -it projekti-web python manage.py loaddata ~/all_dump.json

python manage.py dumpdata auth.user --indent 2 -o fixturas.json

# Delete from file {
#     "model": "accounts.profile",
#     "pk": 39,
#     "fields": {
#         "user": 17,
#         ...
#     }
# }

python manage.py shell -c "from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
```

# Load fixturas.json:
```bash
python manage.py loaddata fixturas.json
```

# IF You use docker-compose localy:
```bash

# comment docker-compose.yml Cloudflare section

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
# python manage.py dumpdata auth.user accounts projects teams tasks notifications comments --indent 4 -o fixturas.json
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

# Apturēt visus projekta konteinerus
docker ps -q | xargs -r docker stop
docker stop $(docker ps -q)
# Izdzēst visus konteinerus
docker ps -aq | xargs -r docker rm
# IZDZĒST VISUS VOLUMES (Šis izdzēsīs veco Postgres datus ar kļūdaino recipient_id)
docker volume prune -f
# Drošībai izdzēst vecos image, lai GitHub Workflow būvē visu no jauna
docker image prune -a -f
```

# Read logs
```bash
docker logs projekti-web
docker logs projekti-postgresdb
```

#
```bash
docker exec -it projekti-web python manage.py migrate
docker exec -it projekti-web python manage.py collectstatic --noinput
docker exec -it projekti-web python manage.py loaddata fixturas.json
```

# Migrate to new server

```bash
# Dump database from old server :
docker exec -e PGPASSWORD='YOUR_PASSWORD' DOCKER_NAME pg_dump -U YourUSER YourDatabase > ~/dump_$(date +%Y-%m-%d_%H_%M_%S).sql

# Create fixturas
python manage.py dumpdata auth.user --indent 2 -o fixturas.json

docker exec -it projekti-web python manage.py dumpdata auth.group > ~/groups_and_perms.json

# Groups and Perms
docker exec -it projekti-web psql -U YourUser -d YourDatabase -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO YourUser; GRANT ALL ON SCHEMA public TO public;"

# Back to database:
docker exec -i DOCKER_NAME /bin/bash -c "PGPASSWORD='YOUR_PASSWORD' psql --username YourUSER YourDatabase" < ~/dump_$(date +%Y-%m-%d_%H_%M_%S).sql

sudo docker exec -it projekti-web python manage.py migrate

docker exec -i projekti-web python manage.py loaddata - --format=json < ~/groups_and_perms.json

# Copy json from docker
docker cp DOCKER_NAME:/usr/src/app/fixturas.json /home/wolf

# Copy json to docker
docker cp ~/fixturas.json DOCKER_NAME:/usr/src/app/

# Login in docker
docker exec -it DOCKER_NAME /bin/bash

# Load data to docker
docker exec -it DOCKER_NAME python manage.py loaddata fixturas.json

# Back to database:
sudo docker exec -i DOCKER_NAME python manage.py loaddata - --format=json < ~/fixturas.json

# Create super user in docker
python manage.py createsuperuser

# Only one docker build
docker-compose up -d --no-deps --build projekti-web

# DOCKER_NAME
DOCKER_NAME = projekti-web 
```
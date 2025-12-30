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
   ```

### **Project Structure**

```
Mifrate Server:

python manage.py shell
# Inside shell:
from django.apps import apps
print([app.label for app in apps.get_app_configs()])

['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'tempus_dominus', 'crispy_forms', 'crispy_bootstrap5', 'django_celery_beat', 'phonenumber_field', 'accounts', 'projects', 'tasks', 'notifications', 'teams', 'comments']
```

```
Create fixturas:

python manage.py dumpdata auth.user accounts projects teams tasks notifications comments --indent 4 -o fixturas.json

python manage.py shell -c "from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"
```

   Load fixturas.json:
   ```bash
   python manage.py loaddata fixturas.json
   ```
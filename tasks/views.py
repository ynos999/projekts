from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
import json
from django.http import JsonResponse
from .models import Task
from projects.models import Project
from .forms import TaskUpdateForm, TaskUserAssignmentForm, TaskForm
from notifications.tasks import create_notification

from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from datetime import datetime

from django.core.mail import send_mail
from django.conf import settings


@require_POST
@csrf_exempt
def update_task_status_ajax(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id)
        raw_status = request.POST.get('status', '').lower().strip()
        
        # Apvienota un droša vārdnīca
        status_map = {
            'backlog': 'Backlog',
            'todo': 'To Do',
            'to do': 'To Do',
            'inprogress': 'In Progress',
            'in progress': 'In Progress',
            'completed': 'Completed',
            'done': 'Completed'
        }
        
        new_status = status_map.get(raw_status)
        
        if new_status:
            task.status = new_status
            task.save()
            # Šis print apstiprinās, ka DB operācija notika
            print(f"DEBUG: Veiksmīgi saglabāts DB: ID {task.id} -> {task.status}")
            return JsonResponse({'success': True, 'new_status': task.status})
        
        print(f"DEBUG: KĻŪDA! '{raw_status}' netika atrasts status_map")
        return JsonResponse({'success': False, 'error': f'Invalid status: {raw_status}'}, status=400)
            
    return JsonResponse({'success': False}, status=405)


@require_POST
def create_task_ajax(request):
    name = request.POST.get('name')
    project_id = request.POST.get('project_id')
    user = request.user

    if not name:
        return JsonResponse({'success': False, 'error': 'Task title is required'})
    
    if not project_id:
        return JsonResponse({'success': False, 'error': 'Project ID is required'})
    
    try:
        project = Project.objects.get(id=project_id)

        # create new task
        new_task = Task.objects.create(name=name, project=project, owner=user)

        return JsonResponse({'success': True, 'task_id': new_task.id})
    except Project.DoesNotExist:
         return JsonResponse({'success': False, 'error': 'Project not found'})
    


def get_task(request, task_id):
    # get by id
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, stutus=404)
    
    if request.method == "GET":
         # construct a json response
         task_data =  {
             "task_id": str(task.id),
             "name": task.name,
             "description": task.description,
            "priority": task.priority,
             "start_date": task.start_date.isoformat() if task.start_date else "",
             "due_date": task.due_date.isoformat() if task.due_date else "",
         }

         return JsonResponse({"task_data": task_data})
    

def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()

            # return response
            return JsonResponse({
            'success': True,
            'updatedTask':  {
             "id": str(task.id),
             "name": task.name,
             "description": task.description,
             "start_date": task.start_date.isoformat() if task.start_date else "",
             "due_date": task.due_date.isoformat() if task.due_date else "",
         }
            })
        else:
            # return form errors
            return JsonResponse({'success': False, 'error': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def assign_user_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
       form = TaskUserAssignmentForm(request.POST, instance=task)
       if form.is_valid():
        #    save form
        task = form.save()

        # send notifications to the user
        actor_username = request.user.username
        task_user_profile = task.user_assigned_to.profile
        verb = f"Dear {task_user_profile.full_name}, {task.name} is assigned to you. Kindly take neccessary steps to attend to it."
        object_id = task.id
        
        create_notification(
                            actor_username =actor_username, 
                            verb=verb, 
                            object_id=object_id, 
                            content_type_model = "task", 
                            content_type_app_label = "tasks"
                            )
        return JsonResponse({
            'success': True,
            'user': {
                'id': task.user_assigned_to.id,
                'name': task.user_assigned_to.profile.full_name,
                'profile_picture_url': task.user_assigned_to.profile.profile_picture_url
            }
            })          

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def get_task_assignment_form(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        form = TaskUserAssignmentForm(initial={
            'task_id': task.id,
            'user_assigned_to': task.user_assigned_to.id if task.user_assigned_to else None
            })
        html = render_to_string('tasks/task_assignment_form.html', {'form': form, 'task': task})
        return JsonResponse({'html': html})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    def get_queryset(self):
        # 1. Pamata filtrs (Lomas noteikšana)
        if self.request.user.is_staff:
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(
                Q(owner=self.request.user) | Q(user_assigned_to=self.request.user)
            )
        
        query = self.request.GET.get('q')

        if query:
            parsed_date = None
            try:
                parsed_date = datetime.strptime(query, "%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError:
                pass

            # 2. Teksta meklēšana (strādā uz jau nofiltrētā queryset)
            queryset = queryset.annotate(
                due_date_str=Cast('due_date', CharField())
            ).filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(project__name__icontains=query) |
                Q(status__icontains=query) |
                Q(due_date_str__icontains=query)
            )

            # 3. Datuma meklēšanas papildinājums
            if parsed_date:
                # Šeit mēs izmantojam to pašu sākuma loģiku:
                if self.request.user.is_staff:
                    # Adminam meklējam datumu visā bāzē
                    date_filter = Q(due_date=parsed_date)
                else:
                    # Lietotājam meklējam datumu tikai viņa atļautajos uzdevumos
                    date_filter = Q(due_date=parsed_date) & (
                        Q(owner=self.request.user) | Q(user_assigned_to=self.request.user)
                    )
                
                queryset = queryset | Task.objects.filter(date_filter)
        
        return queryset.distinct().order_by('due_date')
    
class ActiveTaskListView(TaskListView):
    def get_queryset(self):
        # Papildus filtrējam, lai rādītu tikai nepabeigtos
        return super().get_queryset().exclude(status='Completed')


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskUpdateForm  # Izmanto jau importēto formu
    # form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Paziņojuma nosūtīšana
        actor_username = self.request.user.username
        verb = f'Tev piešķirts jauns uzdevums: {self.object.name}'

        create_notification(
            actor_username=actor_username,
            verb=verb,
            object_id=self.object.id,
            content_type_model="task",
            content_type_app_label="tasks"
        )
        
        if self.object.user_assigned_to and self.object.user_assigned_to.email:
            subject = f"Jauns uzdevums: {self.object.name}"
            message = f"Sveiki, {self.object.user_assigned_to.username}!\n\nJums ir piešķirts jauns uzdevums: '{self.object.name}' projektā '{self.object.project}'.\nTermiņš: {self.object.due_date}"
            recipient_list = [self.object.user_assigned_to.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
        
        return response


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    # Pēc dzēšanas lietotājs tiks novirzīts atpakaļ uz sarakstu
    success_url = reverse_lazy('tasks:list')
    
    # Šis nodrošina, ka lietotājs var dzēst tikai savus vai projektam piesaistītos uzdevumus (pēc izvēles)
    def get_queryset(self):
        return Task.objects.filter(Q(owner=self.request.user) | Q(user_assigned_to=self.request.user))
        # return Task.objects.filter(owner=self.request.user)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['name', 'project', 'user_assigned_to','description', 'priority', 'status','start_date', 'due_date']
    template_name = 'tasks/task_form.html'  # Pārliecinies, ka šis fails eksistē!
    success_url = reverse_lazy('tasks:list')

    def get_queryset(self):
        return Task.objects.filter(Q(owner=self.request.user) | Q(user_assigned_to=self.request.user))
        # return Task.objects.filter(owner=self.request.user)
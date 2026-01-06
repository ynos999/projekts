from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from .models import Project
from .forms import ProjectForm, AttachmentForm
from comments.models import Comment
from comments.forms import CommentForm
from tasks.forms import TaskUpdateForm
from notifications.tasks import create_notification
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
# from tasks.models import Task

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create_and_update.html'
    success_url = reverse_lazy('projects:list')

    # ... get_context_data paliek nemainīts ...

    def form_valid(self, form):
        # 1. Piesaistām īpašnieku
        form.instance.owner = self.request.user
        
        # 2. Saglabājam projektu datubāzē
        response = super().form_valid(form)
        
        # 3. Izsaucam paziņojumu sistēmu
        # Šī funkcija automātiski nosūtīs VIENU glītu HTML e-pastu
        create_notification(
            actor_username=self.request.user.username,
            verb=f'Jauns projekts: {self.object.name}',
            object_id=self.object.id,
            content_type_model="project",
            content_type_app_label="projects"
        )
        
        # VISU TRY/EXCEPT BLOKU AR SEND_MAIL ŠEIT VAJAG IZDZĒST
        
        return response
    

class ProjectListView(ListView):
    model = Project
    context_object_name = "projects"
    template_name = "projects/project_list.html"
    paginate_by = 5

def get_queryset(self):
    # 1. Pamata queryset - atļaujam gan īpašniekam, gan komandas biedriem
    # Pārliecinies, ka Q ir importēts (from django.db.models import Q)
    queryset = Project.objects.filter(
        Q(owner=self.request.user) | Q(team__members=self.request.user)
    ).distinct()
    
    query = self.request.GET.get('q')
    
    if query:
        parsed_date = None
        try:
            parsed_date = datetime.strptime(query, "%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

        # Filtrējam jau paplašināto queryset
        queryset = queryset.annotate(
            due_date_str=Cast('due_date', CharField())
        ).filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(due_date_str__icontains=query)
        )

        if parsed_date:
            # Pievienojam datuma sakritību, saglabājot piekļuves tiesības
            date_queryset = Project.objects.filter(
                Q(owner=self.request.user) | Q(team__members=self.request.user),
                due_date=parsed_date
            )
            queryset |= date_queryset

    return queryset.distinct().order_by('-created_at')


class MyProjectsListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html' # Izmantojam esošo projektu saraksta veidni
    context_object_name = 'projects'

    def get_queryset(self):
        # Atlasa projektus, kur:
        # 1. Lietotājs ir īpašnieks (owner)
        # VAI
        # 2. Lietotājs ir projektam piesaistītajā komandā
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(team__members=self.request.user)
        ).distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "My projects"
        # context['header_text'] = "My projects"
        return context

def get_context_data(self, **kwargs):
    context = super(ProjectListView, self).get_context_data(**kwargs)
    # Saglabājam paziņojumu loģiku
    latest_notifications = self.request.user.notifications.unread(self.request.user)
    context["latest_notifications"] = latest_notifications[:3]
    context["notification_count"] = latest_notifications.count()
    
    # Saglabājam meklēšanas vārdu formā
    context["search_query"] = self.request.GET.get('q', '')
    
    context["header_text"] = "Projects"
    context["title"] = "All Projects"
    return context

class ProjectNearDueDateListView(ListView):
    model = Project
    context_object_name = "projects"
    template_name = "projects/project_list.html"
    paginate_by = 5

    def get_queryset(self):
        return Project.objects.for_user(self.request.user).due_in_two_days_or_less()

    def get_context_data(self, **kwargs):
        # latest notifications
        context = super(ProjectNearDueDateListView,
                        self).get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread(
            self.request.user)

        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        context["header_text"] = "Due Projects"
        return context

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_create_and_update.html'

    def get_object(self, queryset=None):
        # Tikai iegūstam objektu. Piekļuvi pārbaudīs test_func.
        return get_object_or_404(Project, pk=self.kwargs['pk'])

    def test_func(self):
        # Šeit notiek galvenā piekļuves pārbaude (Īpašnieks vai Admin)
        project = self.get_object()
        return self.request.user == project.owner or self.request.user.is_superuser

    def handle_no_permission(self):
        # Ja test_func atgriež False, lietotājs tiek novirzīts ar paziņojumu
        messages.error(self.request, "Jums nav tiesību labot šo projektu!")
        return redirect('projects:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paziņojumu loģika
        if self.request.user.is_authenticated:
            # Pārliecinies, vai .unread() tiešām prasa lietotāju kā argumentu
            latest_notifications = self.request.user.notifications.unread(self.request.user)
            context["latest_notifications"] = latest_notifications[:3]
            context["notification_count"] = latest_notifications.count()
        
        context.update({
            "header_text": "Project Edit",
            "title": "Project Edit",
            "button_text": "Save changes"
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors and try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('projects:list')

    def get_object(self, queryset=None):
        # get project
        project = get_object_or_404(Project, pk=self.kwargs['pk'])

        # check permission on this project
        if project.owner != self.request.user:
            raise Http404("Project not found.")
        return project

    def get_context_data(self, **kwargs):
        # latest notifications
        context = super(ProjectDeleteView, self).get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        latest_notifications = self.request.user.notifications.unread(
            self.request.user)

        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        context["header_text"] = "Delete Project"
        return context

    def post(self, request, *args, **kwargs):
        # get project and check permissions
        project = self.get_object()

        messages.success(
            request, f"The project {project.name} is deleted successfully.")
        return super().post(request, *args, **kwargs)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project' # Labāka prakse template piekļuvei

    def get_queryset(self):
        # Šis filtrē, kurus objektus lietotājs vispār drīkst redzēt
        from django.db.models import Q
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(team__members=self.request.user)
        ).select_related('owner').prefetch_related('team__members').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Izmantojam jau ielādēto objektu
        project = self.object 
        
        # Paziņojumi (pārliecinies, ka models.py ir salabots, kā runājām sākumā)
        unread_notifications = self.request.user.notifications.filter(read=False)

        comments = Comment.objects.filter_by_instance(project)
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        
        context.update({
            "latest_notifications": unread_notifications[:3],
            "notification_count": unread_notifications.count(),
            "title": project.name,
            "page_obj": paginator.get_page(page_number),
            "comments_count": comments.count(),
            "comment_form": CommentForm(),
            "attachment_form": AttachmentForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        # Svarīgi: self.get_object() izmantos get_queryset filtrus
        # Ja lietotājam nav piekļuves, šeit uzreiz būs 404
        try:
            self.object = self.get_object()
        except:
            messages.error(request, "Jums nav piekļuves šim projektam.")
            return redirect('projects:list')

        project = self.object

        if 'comment_submit' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.content_object = project
                comment.save()

                # Paziņojuma izveide
                create_notification(
                    actor_username=request.user.username,
                    verb=f'{request.user.profile.full_name or request.user.username} komentēja projektu {project.name}',
                    object_id=project.id,
                    content_type_model="project",
                    content_type_app_label="projects"
                )
                messages.success(request, "Komentārs pievienots.")
                return redirect('projects:project-detail', pk=project.pk)

        # ... pārējā post loģika pielikumiem ...
        return self.get(request, *args, **kwargs)

class KanbanBoardView(DetailView):
    model = Project
    template_name = "projects/kanbanboard.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        # latest notifications
        context = super(KanbanBoardView, self).get_context_data(**kwargs)
        latest_notifications = self.request.user.notifications.unread(
            self.request.user)
        project = self.get_object()

        context["latest_notifications"] = latest_notifications[:3]
        context["notification_count"] = latest_notifications.count()
        context["header_text"] = "Kanban Board"
        context["title"] = f"{project.name}'s Kanban Board"
        context["is_kanban"] = True

        # separate tasks by status
        context["backlog_tasks"] = project.tasks.filter(
            status="Backlog").upcoming()
        context["todo_tasks"] = project.tasks.filter(status="To Do").upcoming()
        context["in_progress_tasks"] = project.tasks.filter(
            status="In Progress").upcoming()
        context["completed_tasks"] = project.tasks.filter(
            status="Completed").upcoming()
        context['form'] = TaskUpdateForm()
        # context['task_assignment_form'] = TaskUserAssignmentForm()

        return context

def archive_projects_list(request):
    projects = Project.objects.for_user(request.user).filter(
        due_date__lt=timezone.now().date()
    )
    
    return render(request, 'projects/archive_projects.html', {
        'projects': projects,
        'title': 'Archived Projects'
    })
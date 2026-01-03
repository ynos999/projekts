from django.urls import path
from .views import (
    update_task_status_ajax, 
    create_task_ajax, get_task, 
    update_task, 
    assign_user_to_task, 
    get_task_assignment_form
    )
from django.urls import path
from .views import TaskListView, ActiveTaskListView, TaskCreateView, TaskDeleteView
from . import views


app_name = 'tasks'

urlpatterns = [

# 1. Galvenie saraksti un lapas (HTML)
    path('', views.TaskListView.as_view(), name='list'),
    path('active/', views.ActiveTaskListView.as_view(), name='active-tasks'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<uuid:pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),

    # 2. AJAX operācijas (Datiem fonā)
    # Pārliecinies, ka tavā kanbanboard.html JavaScript tagad izmanto šīs adreses!
    
    path('ajax/create/', views.create_task_ajax, name="create-task-ajax"),
    path('ajax/get/<uuid:task_id>/', views.get_task, name="get_task"),
    path('ajax/assign-user/<uuid:task_id>/', views.assign_user_to_task, name="assign-user"),
    path('ajax/assignment-form/<uuid:task_id>/', views.get_task_assignment_form, name="assignment-form"),
    path('update-task-status-ajax/<uuid:task_id>/', views.update_task_status_ajax, name='update-task-status-ajax'),

]

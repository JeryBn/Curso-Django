from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("create/", views.task_create, name="task_create"),
]

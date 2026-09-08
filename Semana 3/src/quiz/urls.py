from django.urls import path

from . import views

app_name = "quiz"

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("exams/new/", views.exam_create, name="exam_create"),
    path("exams/<int:exam_id>/", views.exam_detail, name="exam_detail"),
    path(
        "exams/<int:exam_id>/questions/new/",
        views.question_create,
        name="question_create",
    ),
]

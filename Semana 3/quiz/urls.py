from django.urls import path

from quiz import views

app_name = 'quiz'

urlpatterns = [
    # Exámenes
    path('examenes/', views.ExamListView.as_view(), name='exam_list'),
    path('examen/nuevo/', views.ExamCreateView.as_view(), name='exam_create'),
    path('examen/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),

    # Preguntas
    path(
        'examen/<int:exam_id>/pregunta/nueva/',
        views.login_required_question_create,
        name='question_create',
    ),
]

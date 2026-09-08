from django.contrib import admin

from .models import Choice, Exam, Question


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha_creacion")
    search_fields = ("titulo",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("enunciado", "examen", "puntaje", "orden")
    list_filter = ("examen",)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("texto", "pregunta", "correcta")
    list_filter = ("correcta",)

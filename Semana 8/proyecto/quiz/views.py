from django.db import transaction
from django.db.models import Count
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, serializers, viewsets

from .models import Choice, Exam, Question
from .serializers import (
    ChoiceResourceSerializer, ExamSerializer, QuestionSerializer,
)


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    queryset = Exam.objects.annotate(question_count=Count("questions")).order_by("id")


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter("exam", int, description="Solo las preguntas de este examen."),
        ]
    )
)
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_queryset(self):
        queryset = Question.objects.select_related("exam").prefetch_related("choices")
        exam = self.request.query_params.get("exam")
        if exam and exam.isdigit():
            queryset = queryset.filter(exam_id=int(exam))
        return queryset


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceResourceSerializer
    queryset = Choice.objects.select_related("question", "question__exam")

    @transaction.atomic
    def perform_destroy(self, instance):
        Question.objects.select_for_update().get(pk=instance.question_id)
        remaining = Choice.objects.filter(question_id=instance.question_id).exclude(
            pk=instance.pk
        )
        if remaining.count() < 2:
            raise serializers.ValidationError(
                "Una pregunta necesita al menos dos opciones."
            )
        if remaining.filter(is_correct=True).count() != 1:
            raise serializers.ValidationError(
                "Debe haber exactamente una opción correcta."
            )
        instance.delete()

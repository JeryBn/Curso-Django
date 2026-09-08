from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ChoiceFormSet, ExamForm, QuestionForm
from .models import Choice, Exam, Question


@require_http_methods(["GET"])
def exam_list(request):
    """Display all exams in their model-defined order."""
    exams = Exam.objects.all()
    return render(request, "quiz/exam_list.html", {"exams": exams})


@require_http_methods(["GET"])
def exam_detail(request, exam_id):
    """Display an exam and all of its questions and choices."""
    questions = Question.objects.prefetch_related(
        Prefetch("choices", queryset=Choice.objects.all())
    )
    exam = get_object_or_404(
        Exam.objects.prefetch_related(Prefetch("questions", queryset=questions)),
        pk=exam_id,
    )
    return render(request, "quiz/exam_detail.html", {"exam": exam})


@require_http_methods(["GET", "POST"])
def exam_create(request):
    """Create an exam using the POST-Redirect-GET pattern."""
    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        exam = form.save()
        return redirect("quiz:exam_detail", exam_id=exam.pk)

    return render(
        request,
        "quiz/exam_form.html",
        {"form": form, "page_title": "Crear examen"},
    )


@require_http_methods(["GET", "POST"])
def question_create(request, exam_id):
    """Create a question and its choices for an existing exam."""
    exam = get_object_or_404(Exam, pk=exam_id)
    question = Question(exam=exam)
    form = QuestionForm(request.POST or None, instance=question)
    formset = ChoiceFormSet(request.POST or None, instance=question)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            question = form.save()
            formset.instance = question
            formset.save()
        return redirect(reverse("quiz:exam_detail", kwargs={"exam_id": exam.pk}))

    return render(
        request,
        "quiz/question_form.html",
        {
            "exam": exam,
            "form": form,
            "formset": formset,
            "page_title": "Añadir pregunta",
        },
    )

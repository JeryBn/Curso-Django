from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Choice, Exam, Question


class ExamForm(forms.ModelForm):
    """Create or update an exam."""

    class Meta:
        model = Exam
        fields = ("title", "description")
        labels = {
            "title": "Título",
            "description": "Descripción",
        }


class QuestionForm(forms.ModelForm):
    """Create or update a question belonging to an exam."""

    class Meta:
        model = Question
        fields = ("prompt", "score")
        labels = {
            "prompt": "Enunciado",
            "score": "Puntuación",
        }


class ChoiceForm(forms.ModelForm):
    """Create or update a choice belonging to a question."""

    class Meta:
        model = Choice
        fields = ("text", "is_correct")
        labels = {
            "text": "Texto",
            "is_correct": "Respuesta correcta",
        }


class BaseChoiceInlineFormSet(BaseInlineFormSet):
    """Require one, and only one, valid choice to be correct."""

    def clean(self):
        super().clean()

        correct_choices = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE") or form.errors:
                continue

            if form.cleaned_data.get("is_correct"):
                correct_choices += 1

        if correct_choices != 1:
            raise forms.ValidationError(
                "Debe marcar exactamente una opción válida como correcta."
            )


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    formset=BaseChoiceInlineFormSet,
    fields=("text", "is_correct"),
    extra=4,
    can_delete=True,
)

from django.db import models


class Exam(models.Model):
    """A collection of questions."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "title")
        verbose_name = "examen"
        verbose_name_plural = "exámenes"

    def __str__(self):
        return self.title


class Question(models.Model):
    """A question associated with an exam."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt = models.TextField()
    score = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("pk",)
        verbose_name = "pregunta"
        verbose_name_plural = "preguntas"

    def __str__(self):
        return self.prompt


class Choice(models.Model):
    """A selectable answer for a question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ("pk",)
        verbose_name = "opción"
        verbose_name_plural = "opciones"

    def __str__(self):
        return self.text

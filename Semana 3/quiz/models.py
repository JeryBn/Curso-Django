from django.db import models
from django.utils import timezone


class Exam(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'examen'
        verbose_name_plural = 'examenes'

    def __str__(self):
        return self.titulo


class Question(models.Model):
    enunciado = models.TextField()
    examen = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='preguntas'
    )
    orden = models.IntegerField(default=0)
    puntaje = models.IntegerField(default=10)

    class Meta:
        ordering = ['orden']
        verbose_name = 'pregunta'
        verbose_name_plural = 'preguntas'

    def __str__(self):
        return self.enunciado


class Choice(models.Model):
    texto = models.CharField(max_length=300)
    correcta = models.BooleanField(default=False)
    pregunta = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='opciones'
    )
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'opcion'
        verbose_name_plural = 'opciones'

    def __str__(self):
        return self.texto

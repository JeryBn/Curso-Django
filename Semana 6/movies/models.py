from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("última modificación", auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    name = models.CharField("nombre", max_length=80, unique=True)
    description = models.TextField("descripción", blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "género"
        verbose_name_plural = "géneros"

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    first_name = models.CharField("nombres", max_length=100)
    last_name = models.CharField("apellidos", max_length=100)
    birth_date = models.DateField("fecha de nacimiento", blank=True, null=True)
    biography = models.TextField("biografía", blank=True)
    photo = models.ImageField("fotografía", upload_to="people/", blank=True)

    class Meta:
        ordering = ("last_name", "first_name")
        verbose_name = "persona"
        verbose_name_plural = "personas"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Movie(TimeStampedModel):
    title = models.CharField("título", max_length=200)
    synopsis = models.TextField("sinopsis")
    release_year = models.PositiveSmallIntegerField(
        "año de estreno",
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
    )
    duration_minutes = models.PositiveSmallIntegerField(
        "duración en minutos",
        validators=[MinValueValidator(1), MaxValueValidator(600)],
    )
    poster = models.ImageField("póster", upload_to="posters/", blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", verbose_name="géneros")
    director = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="directed_movies",
        verbose_name="director",
    )
    cast = models.ManyToManyField(
        Person,
        related_name="acting_movies",
        verbose_name="reparto",
        blank=True,
    )

    class Meta:
        ordering = ("title",)
        constraints = [
            models.UniqueConstraint(
                fields=("title", "release_year"),
                name="unique_movie_title_per_year",
            )
        ]
        verbose_name = "película"
        verbose_name_plural = "películas"

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Rating(TimeStampedModel):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="película",
    )
    reviewer_name = models.CharField("nombre del crítico", max_length=120)
    score = models.PositiveSmallIntegerField(
        "puntuación",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("comentario", blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("movie", "reviewer_name"),
                name="unique_rating_per_reviewer_and_movie",
            )
        ]
        verbose_name = "valoración"
        verbose_name_plural = "valoraciones"

    def __str__(self):
        return f"{self.movie.title}: {self.score}/5 por {self.reviewer_name}"

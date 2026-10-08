from django.db import models
from django.urls import reverse
from django.utils import timezone

from movies.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField("descripción", blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("news:category", args=[self.slug])


class Author(TimeStampedModel):
    name = models.CharField("nombre", max_length=120)
    biography = models.TextField("biografía", blank=True)
    photo = models.ImageField("fotografía", upload_to="authors/", blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.name


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Article(TimeStampedModel):
    title = models.CharField("título", max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField("resumen")
    body = models.TextField("cuerpo")
    featured_image = models.ImageField(
        "imagen destacada", upload_to="articles/", blank=True
    )
    published_at = models.DateTimeField("fecha de publicación", default=timezone.now)
    is_published = models.BooleanField("publicado", default=False)
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="articles", verbose_name="autor"
    )
    categories = models.ManyToManyField(
        Category, related_name="articles", verbose_name="categorías"
    )
    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ("-published_at", "-pk")
        verbose_name = "noticia"
        verbose_name_plural = "noticias"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", args=[self.slug])

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "pk"]
        verbose_name = "author"
        verbose_name_plural = "authors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AuthorProfile(models.Model):
    author = models.OneToOneField(
        Author,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    photo = models.ImageField(upload_to="authors/%Y/%m/", blank=True)

    class Meta:
        ordering = ["author__last_name", "author__first_name", "pk"]
        verbose_name = "author profile"
        verbose_name_plural = "author profiles"

    def __str__(self):
        return f"Profile: {self.author}"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=150, unique=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "publisher"
        verbose_name_plural = "publishers"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"\A[0-9]{13}\Z",
                message=(
                    "Enter an ISBN with exactly 13 digits, without hyphens."
                ),
            )
        ],
    )
    summary = models.TextField(blank=True)
    cover = models.ImageField(upload_to="books/%Y/%m/", blank=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
    )
    categories = models.ManyToManyField(
        Category,
        related_name="books",
        blank=True,
    )
    publishers = models.ManyToManyField(
        Publisher,
        through="Publication",
        related_name="books",
        blank=True,
    )

    class Meta:
        ordering = ["title", "pk"]
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("library:book_detail", kwargs={"pk": self.pk})


class Publication(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="publications",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name="publications",
    )
    publication_date = models.DateField()
    edition = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["book__title", "publisher__name", "edition"]
        verbose_name = "publication"
        verbose_name_plural = "publications"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "publisher", "edition"],
                name="unique_book_publisher_edition",
            ),
            models.CheckConstraint(
                condition=models.Q(edition__gte=1),
                name="publication_edition_gte_1",
            ),
        ]

    def __str__(self):
        return f"{self.book} - {self.publisher} (edition {self.edition})"

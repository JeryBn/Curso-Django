from datetime import date
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)


class SampleDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_library", stdout=StringIO())
        cls.book = Book.objects.get(isbn="9780307474728")
        cls.author = cls.book.author
        cls.category = Category.objects.get(name="Realismo mágico")
        cls.publisher = Publisher.objects.get(name="Editorial Horizonte")


class RelationshipTests(SampleDataTestCase):
    def test_author_relationship_in_both_directions(self):
        self.assertEqual(str(self.book.author), "Gabriel García Márquez")
        self.assertQuerySetEqual(
            self.author.books.all(),
            ["Cien años de soledad", "El amor en los tiempos del cólera"],
            transform=str,
        )

    def test_profile_relationship_is_one_to_one(self):
        self.assertEqual(self.author.profile.author, self.author)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AuthorProfile.objects.create(author=self.author)

    def test_category_relationship_in_both_directions(self):
        self.assertEqual(self.book.categories.count(), 2)
        self.assertIn(self.category, self.book.categories.all())
        self.assertIn(self.book, self.category.books.all())
        books = Book.objects.filter(
            categories__in=self.book.categories.all()
        ).distinct()
        self.assertEqual(books.filter(pk=self.book.pk).count(), 1)

    def test_through_data_is_available_from_both_sides(self):
        self.assertEqual(self.book.publishers.count(), 2)
        self.assertIn(self.book, self.publisher.books.all())
        publication = self.book.publications.get(publisher=self.publisher)
        self.assertEqual(publication.publication_date, date(2024, 6, 1))
        self.assertEqual(publication.edition, 2)
        self.assertEqual(
            self.publisher.publications.get(book=self.book), publication
        )

    def test_author_with_books_is_protected_without_partial_deletion(self):
        with self.assertRaises(ProtectedError) as error:
            self.author.delete()
        self.assertEqual(len(error.exception.protected_objects), 2)
        self.author.refresh_from_db()
        self.assertEqual(self.author.books.count(), 2)
        self.assertTrue(AuthorProfile.objects.filter(author=self.author).exists())
        self.assertEqual(Publication.objects.count(), 5)
        self.assertEqual(Book.categories.through.objects.count(), 8)

    def test_author_without_books_cascades_to_profile(self):
        author = Author.objects.create(first_name="Test", last_name="Author")
        profile = AuthorProfile.objects.create(author=author)
        author.delete()
        self.assertFalse(AuthorProfile.objects.filter(pk=profile.pk).exists())

    def test_book_deletion_cascades_only_to_its_dependent_rows(self):
        book_pk = self.book.pk
        self.book.delete()
        self.assertFalse(Publication.objects.filter(book_id=book_pk).exists())
        self.assertFalse(
            Book.categories.through.objects.filter(book_id=book_pk).exists()
        )
        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Publisher.objects.count(), 2)

    def test_publisher_with_publications_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.publisher.delete()
        self.assertEqual(Publication.objects.count(), 5)

    def test_category_deletion_removes_links_and_keeps_books(self):
        self.category.delete()
        self.assertEqual(Book.objects.count(), 4)
        self.assertEqual(self.book.categories.count(), 1)

    def test_publication_rejects_duplicate_edition_at_database_level(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Publication.objects.create(
                book=self.book,
                publisher=self.publisher,
                publication_date=date(2025, 1, 1),
                edition=2,
            )

    def test_publication_rejects_zero_edition_at_database_level(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Publication.objects.create(
                book=self.book,
                publisher=self.publisher,
                publication_date=date(2025, 1, 1),
                edition=0,
            )

    def test_same_book_and_publisher_can_have_another_edition(self):
        Publication.objects.create(
            book=self.book,
            publisher=self.publisher,
            publication_date=date(2025, 1, 1),
            edition=3,
        )
        self.assertEqual(
            self.book.publications.filter(publisher=self.publisher).count(), 2
        )
        self.assertEqual(self.book.publishers.distinct().count(), 2)

    def test_isbn_validation_rejects_invalid_format(self):
        self.book.isbn = "invalid-isbn"
        with self.assertRaises(ValidationError) as error:
            self.book.full_clean()
        self.assertIn("isbn", error.exception.message_dict)


class CatalogTests(SampleDataTestCase):
    def test_catalog_renders_sample_books_and_counts(self):
        response = self.client.get(reverse("library:book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["book_count"], 4)
        self.assertEqual(response.context["author_count"], 2)
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.get_absolute_url())

    def test_search_and_category_filters(self):
        cases = [
            ({"q": "Gabriel"}, 2),
            ({"q": self.book.isbn}, 1),
            ({"category": self.category.pk}, 2),
            ({"q": "Isabel", "category": self.category.pk}, 1),
            ({"q": "No matching book"}, 0),
        ]
        for params, expected_count in cases:
            with self.subTest(params=params):
                response = self.client.get(
                    reverse("library:book_list"), params
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.context["paginator"].count, expected_count
                )

    def test_invalid_filters_show_form_errors(self):
        for params in (
            {"category": "invalid"},
            {"category": "99999999"},
            {"q": "x" * 121},
        ):
            with self.subTest(params=params):
                response = self.client.get(
                    reverse("library:book_list"), params
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["filter_form"].errors)
                self.assertEqual(response.context["paginator"].count, 0)

    def test_detail_renders_related_data_in_three_queries(self):
        with self.assertNumQueries(3):
            response = self.client.get(self.book.get_absolute_url())
        for text in (
            "Gabriel García Márquez",
            "Colombia",
            "Premio Nobel",
            "Realismo mágico",
            "Editorial Horizonte",
            "Editorial Sur",
            "01/06/2024",
            "15/05/2020",
            "2.ª",
        ):
            self.assertContains(response, text)

    def test_detail_handles_optional_relations_and_escapes_summary(self):
        author = Author.objects.create(first_name="New", last_name="Author")
        book = Book.objects.create(
            title="A new book",
            isbn="9000000000001",
            author=author,
            summary="<script>alert('example')</script>",
        )
        response = self.client.get(book.get_absolute_url())
        self.assertContains(response, "Sin categorías asignadas")
        self.assertContains(response, "aún no tiene un perfil biográfico")
        self.assertContains(
            response, "Todavía no se han registrado publicaciones"
        )
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")

    def test_missing_book_returns_not_found(self):
        response = self.client.get(
            reverse("library:book_detail", kwargs={"pk": 999999})
        )
        self.assertEqual(response.status_code, 404)

    def test_empty_catalog_explains_how_to_add_books(self):
        Book.objects.all().delete()
        response = self.client.get(reverse("library:book_list"))
        self.assertContains(response, "La colección está por comenzar")
        self.assertContains(response, reverse("admin:library_book_add"))

    def test_pagination_preserves_search_and_category(self):
        for index in range(9):
            book = Book.objects.create(
                title=f"Pagination {index}",
                isbn=str(9000000000000 + index),
                author=self.author,
            )
            book.categories.add(self.category)
        params = {"q": "Pagination", "category": self.category.pk}
        response = self.client.get(reverse("library:book_list"), params)
        self.assertEqual(len(response.context["books"]), 8)
        self.assertContains(
            response,
            f"q=Pagination&amp;category={self.category.pk}&amp;page=2#collection",
        )
        response = self.client.get(
            reverse("library:book_list"), {**params, "page": 2}
        )
        self.assertEqual(len(response.context["books"]), 1)


class AdminTests(SampleDataTestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="test-admin", is_staff=True, is_superuser=True
        )
        self.client.force_login(user)

    def test_admin_creates_book_with_categories_publication_and_image(self):
        image = BytesIO()
        Image.new("RGB", (20, 30), color="green").save(image, format="PNG")
        upload = SimpleUploadedFile(
            "cover.png", image.getvalue(), content_type="image/png"
        )
        with TemporaryDirectory() as directory:
            with self.settings(MEDIA_ROOT=directory):
                response = self.client.post(
                    reverse("admin:library_book_add"),
                    {
                        "title": "Admin book",
                        "isbn": "9000000000010",
                        "author": self.author.pk,
                        "categories": [self.category.pk],
                        "cover": upload,
                        "publications-TOTAL_FORMS": "1",
                        "publications-INITIAL_FORMS": "0",
                        "publications-MIN_NUM_FORMS": "0",
                        "publications-MAX_NUM_FORMS": "1000",
                        "publications-0-publisher": self.publisher.pk,
                        "publications-0-publication_date": "2024-01-01",
                        "publications-0-edition": "1",
                        "_save": "Save",
                    },
                )
                self.assertRedirects(
                    response, reverse("admin:library_book_changelist")
                )
                book = Book.objects.get(isbn="9000000000010")
                self.assertIn(self.category, book.categories.all())
                self.assertEqual(
                    book.publications.get().publisher, self.publisher
                )
                self.assertTrue(book.cover.storage.exists(book.cover.name))
                response = self.client.get(book.get_absolute_url())
                self.assertContains(response, book.cover.url)

    def test_admin_creates_author_with_profile_inline(self):
        response = self.client.post(
            reverse("admin:library_author_add"),
            {
                "first_name": "New",
                "last_name": "Writer",
                "profile-TOTAL_FORMS": "1",
                "profile-INITIAL_FORMS": "0",
                "profile-MIN_NUM_FORMS": "0",
                "profile-MAX_NUM_FORMS": "1",
                "profile-0-biography": "An example biography.",
                "profile-0-country": "Peru",
                "_save": "Save",
            },
        )
        self.assertRedirects(
            response, reverse("admin:library_author_changelist")
        )
        author = Author.objects.get(first_name="New", last_name="Writer")
        self.assertEqual(author.profile.biography, "An example biography.")

    def test_admin_blocks_deleting_author_with_books(self):
        response = self.client.post(
            reverse("admin:library_author_delete", args=[self.author.pk]),
            {"post": "yes"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())
        self.assertEqual(Book.objects.count(), 4)


class LaboratoryCommandTests(SampleDataTestCase):
    models = (
        Author,
        AuthorProfile,
        Book,
        Category,
        Publisher,
        Publication,
        Book.categories.through,
    )

    def snapshot(self):
        return {
            model._meta.label: list(model.objects.order_by("pk").values())
            for model in self.models
        }

    def test_seed_is_idempotent_and_preserves_edits(self):
        self.book.summary = "An edited summary."
        self.book.save()
        before = self.snapshot()
        call_command("seed_library", stdout=StringIO())
        self.assertEqual(self.snapshot(), before)

    def test_inspect_relations_prints_actual_results(self):
        output = StringIO()
        call_command("inspect_relations", stdout=output)
        self.assertIn("Gabriel García Márquez", output.getvalue())
        self.assertIn("datetime.date(2024, 6, 1), 2", output.getvalue())
        self.assertIn("library_book_categories", output.getvalue())

    def test_inspect_relations_explains_missing_sample_data(self):
        self.book.delete()
        with self.assertRaises(CommandError):
            call_command("inspect_relations", stdout=StringIO())

    def test_compare_deletions_executes_both_policies_and_rolls_back(self):
        before = self.snapshot()
        output = StringIO()
        call_command("compare_deletions", stdout=output)
        result = output.getvalue()
        self.assertIn("CASCADE (library.0001_initial)", result)
        self.assertIn("Deleted rows: 5", result)
        self.assertIn(
            "Author=0, AuthorProfile=0, Book=0, Publication=0", result
        )
        self.assertIn("PROTECT (library.0002_protect_book_author)", result)
        self.assertIn("ProtectedError: 1 book(s) prevent deletion.", result)
        self.assertIn(
            "Author=1, AuthorProfile=1, Book=1, Publication=1", result
        )
        self.assertEqual(self.snapshot(), before)

    def test_schema_contains_the_implicit_and_explicit_join_tables(self):
        tables = {
            name
            for name in connection.introspection.table_names()
            if name.startswith("library_")
        }
        self.assertEqual(
            tables,
            {
                "library_author",
                "library_authorprofile",
                "library_book",
                "library_book_categories",
                "library_category",
                "library_publication",
                "library_publisher",
            },
        )

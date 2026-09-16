from datetime import date
from uuid import uuid4

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.models.deletion import ProtectedError


class Command(BaseCommand):
    help = (
        "Compare CASCADE and PROTECT with historical migration models. "
        "All temporary records and deletions are rolled back."
    )
    requires_migrations_checks = True

    def handle(self, *args, **options):
        loader = MigrationLoader(connection)
        for migration_name in (
            "0001_initial",
            "0002_protect_book_author",
        ):
            apps = loader.project_state([("library", migration_name)]).apps
            author_model = apps.get_model("library", "Author")
            profile_model = apps.get_model("library", "AuthorProfile")
            book_model = apps.get_model("library", "Book")
            category_model = apps.get_model("library", "Category")
            publisher_model = apps.get_model("library", "Publisher")
            publication_model = apps.get_model("library", "Publication")
            author_field = book_model._meta.get_field("author")
            policy = author_field.remote_field.on_delete

            self.stdout.write(f"{policy.__name__} (library.{migration_name})")
            with transaction.atomic():
                token = uuid4()
                author = author_model.objects.create(
                    first_name="Deletion", last_name=f"Example {token.hex}"
                )
                profile = profile_model.objects.create(author=author)
                book = book_model.objects.create(
                    title="Temporary deletion example",
                    isbn=f"{token.int % 10**13:013d}",
                    author=author,
                )
                category = category_model.objects.create(
                    name=f"Temporary category {token.hex}"
                )
                publisher = publisher_model.objects.create(
                    name=f"Temporary publisher {token.hex}"
                )
                book.categories.add(category)
                publication = publication_model.objects.create(
                    book=book,
                    publisher=publisher,
                    publication_date=date(2024, 1, 1),
                    edition=1,
                )
                records = (
                    ("Author", author_model, author.pk),
                    ("AuthorProfile", profile_model, profile.pk),
                    ("Book", book_model, book.pk),
                    ("Publication", publication_model, publication.pk),
                    ("Category", category_model, category.pk),
                    ("Publisher", publisher_model, publisher.pk),
                )
                book_pk = book.pk

                try:
                    deleted_count, _ = author.delete()
                    self.stdout.write(f"Deleted rows: {deleted_count}")
                except ProtectedError as error:
                    self.stdout.write(
                        "ProtectedError: "
                        f"{len(error.protected_objects)} book(s) "
                        "prevent deletion."
                    )

                remaining = [
                    f"{name}={model.objects.filter(pk=pk).count()}"
                    for name, model, pk in records
                ]
                links = book_model.categories.through.objects.filter(
                    book_id=book_pk
                ).count()
                remaining.append(f"Book_categories={links}")
                self.stdout.write("Remaining: " + ", ".join(remaining))
                transaction.set_rollback(True)
            self.stdout.write("Temporary data rolled back.")

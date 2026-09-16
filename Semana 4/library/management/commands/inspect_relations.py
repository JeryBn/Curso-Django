from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from library.models import Book, Category, Publisher


class Command(BaseCommand):
    help = "Print real ORM queries and their results using the sample books."

    def show(self, expression, result):
        self.stdout.write(f">>> {expression}")
        self.stdout.write(repr(result))

    def handle(self, *args, **options):
        try:
            book = Book.objects.get(isbn="9780307474728")
            category = Category.objects.get(name="Realismo mágico")
            publisher = Publisher.objects.get(name="Editorial Horizonte")
        except (
            Book.DoesNotExist,
            Category.DoesNotExist,
            Publisher.DoesNotExist,
        ):
            raise CommandError(
                "Load the sample data through the admin or run seed_library."
            ) from None

        author = book.author
        self.stdout.write(
            'book = Book.objects.get(isbn="9780307474728")\n'
            "author = book.author\n"
            'category = Category.objects.get(name="Realismo mágico")\n'
            'publisher = Publisher.objects.get(name="Editorial Horizonte")'
        )
        self.show("str(book.author)", str(book.author))
        self.show(
            'list(author.books.values_list("title", flat=True))',
            list(author.books.values_list("title", flat=True)),
        )
        try:
            profile = author.profile
        except AttributeError:
            self.stdout.write("This author has no profile.")
        else:
            self.show("author.profile.country", profile.country)
            self.show("str(author.profile.author)", str(profile.author))

        self.show(
            'list(book.categories.values_list("name", flat=True))',
            list(book.categories.values_list("name", flat=True)),
        )
        self.show(
            'list(category.books.values_list("title", flat=True))',
            list(category.books.values_list("title", flat=True)),
        )
        self.show(
            'list(book.publishers.distinct().values_list("name", flat=True))',
            list(book.publishers.distinct().values_list("name", flat=True)),
        )
        self.show(
            'list(publisher.books.distinct().values_list("title", flat=True))',
            list(publisher.books.distinct().values_list("title", flat=True)),
        )
        self.show(
            'list(book.publications.values_list("publisher__name", '
            '"publication_date", "edition"))',
            list(
                book.publications.values_list(
                    "publisher__name", "publication_date", "edition"
                )
            ),
        )
        self.show(
            'list(publisher.publications.values_list("book__title", '
            '"publication_date", "edition"))',
            list(
                publisher.publications.values_list(
                    "book__title", "publication_date", "edition"
                )
            ),
        )
        self.show(
            'list(Book.objects.filter(author__last_name="García Márquez")'
            '.values_list("title", flat=True))',
            list(
                Book.objects.filter(author__last_name="García Márquez")
                .values_list("title", flat=True)
            ),
        )
        self.show(
            'list(Book.objects.filter(categories__name="Realismo mágico")'
            '.distinct().values_list("title", flat=True))',
            list(
                Book.objects.filter(categories__name="Realismo mágico")
                .distinct()
                .values_list("title", flat=True)
            ),
        )
        self.show(
            'list(Book.objects.filter(publications__edition__gte=2)'
            '.distinct().values_list("title", flat=True))',
            list(
                Book.objects.filter(publications__edition__gte=2)
                .distinct()
                .values_list("title", flat=True)
            ),
        )
        self.show(
            '[name for name in connection.introspection.table_names() '
            'if name.startswith("library_")]',
            [
                name
                for name in connection.introspection.table_names()
                if name.startswith("library_")
            ],
        )

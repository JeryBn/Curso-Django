from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from library.models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)


class Command(BaseCommand):
    help = "Create the laboratory sample data without replacing existing data."

    @transaction.atomic
    def handle(self, *args, **options):
        category_names = [
            "Novela",
            "Realismo mágico",
            "Literatura latinoamericana",
        ]
        categories = {
            name: Category.objects.get_or_create(name=name)[0]
            for name in category_names
        }

        garcia, _ = Author.objects.get_or_create(
            first_name="Gabriel",
            last_name="García Márquez",
        )
        allende, _ = Author.objects.get_or_create(
            first_name="Isabel",
            last_name="Allende",
        )
        AuthorProfile.objects.get_or_create(
            author=garcia,
            defaults={
                "biography": (
                    "Escritor colombiano, referente del realismo mágico y "
                    "ganador del Premio Nobel de Literatura en 1982."
                ),
                "birth_date": date(1927, 3, 6),
                "country": "Colombia",
            },
        )
        AuthorProfile.objects.get_or_create(
            author=allende,
            defaults={
                "biography": (
                    "Escritora chilena nacida en Lima. Sus novelas combinan "
                    "historias familiares, memoria y elementos fantásticos."
                ),
                "birth_date": date(1942, 8, 2),
                "country": "Chile",
            },
        )

        south, _ = Publisher.objects.get_or_create(
            name="Editorial Sur",
            defaults={"country": "Perú"},
        )
        horizon, _ = Publisher.objects.get_or_create(
            name="Editorial Horizonte",
            defaults={"country": "Chile"},
        )

        book_data = [
            (
                "9780307474728",
                "Cien años de soledad",
                garcia,
                "La historia de la familia Buendía a lo largo de varias "
                "generaciones en el pueblo de Macondo.",
                ["Novela", "Realismo mágico"],
                south,
                date(2020, 5, 15),
            ),
            (
                "9780307389732",
                "El amor en los tiempos del cólera",
                garcia,
                "Una historia sobre el amor, la espera y el paso del tiempo "
                "en una ciudad del Caribe.",
                ["Novela", "Literatura latinoamericana"],
                south,
                date(2021, 3, 10),
            ),
            (
                "9781501117015",
                "La casa de los espíritus",
                allende,
                "La vida de la familia Trueba entre recuerdos, cambios "
                "sociales y acontecimientos extraordinarios.",
                ["Novela", "Realismo mágico"],
                horizon,
                date(2022, 8, 2),
            ),
            (
                "9780063021797",
                "Largo pétalo de mar",
                allende,
                "Un viaje de exilio y esperanza que une España y Chile "
                "a través de la vida de sus protagonistas.",
                ["Novela", "Literatura latinoamericana"],
                horizon,
                date(2023, 4, 20),
            ),
        ]

        for (
            isbn,
            title,
            author,
            summary,
            names,
            publisher,
            publication_date,
        ) in book_data:
            book, _ = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    "title": title,
                    "author": author,
                    "summary": summary,
                },
            )
            book.categories.add(*(categories[name] for name in names))
            Publication.objects.get_or_create(
                book=book,
                publisher=publisher,
                edition=1,
                defaults={"publication_date": publication_date},
            )

        Publication.objects.get_or_create(
            book=Book.objects.get(isbn="9780307474728"),
            publisher=horizon,
            edition=2,
            defaults={"publication_date": date(2024, 6, 1)},
        )

        self.stdout.write(self.style.SUCCESS("Sample data is ready."))
        for model in (
            Author,
            AuthorProfile,
            Book,
            Category,
            Publisher,
            Publication,
        ):
            self.stdout.write(f"{model.__name__}: {model.objects.count()}")

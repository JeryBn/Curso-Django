import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from movies.models import Genre, Movie, Person, Rating


GENRES = {
    "Ciencia ficción": "Historias especulativas sobre ciencia, tecnología y futuros posibles.",
    "Drama": "Relatos centrados en conflictos humanos y evolución de personajes.",
    "Animación": "Obras creadas principalmente mediante técnicas de animación.",
    "Aventura": "Viajes, exploración y desafíos en escenarios extraordinarios.",
}

PEOPLE = [
    ("Christopher", "Nolan"),
    ("Denis", "Villeneuve"),
    ("Greta", "Gerwig"),
    ("Hayao", "Miyazaki"),
    ("Ryan", "Coogler"),
    ("Céline", "Sciamma"),
    ("Alfonso", "Cuarón"),
    ("Patty", "Jenkins"),
]

MOVIES = [
    {
        "title": "Horizonte de acero",
        "year": 2024,
        "duration": 142,
        "director": ("Denis", "Villeneuve"),
        "genres": ("Ciencia ficción", "Aventura"),
        "cast": (("Patty", "Jenkins"), ("Ryan", "Coogler")),
        "synopsis": "Una tripulación científica cruza un corredor espacial para salvar su colonia.",
    },
    {
        "title": "El último faro",
        "year": 2021,
        "duration": 118,
        "director": ("Céline", "Sciamma"),
        "genres": ("Drama",),
        "cast": (("Greta", "Gerwig"),),
        "synopsis": "Una guardiana enfrenta la última noche de servicio y una decisión familiar.",
    },
    {
        "title": "Ciudad de papel",
        "year": 2020,
        "duration": 104,
        "director": ("Greta", "Gerwig"),
        "genres": ("Drama", "Aventura"),
        "cast": (("Céline", "Sciamma"), ("Ryan", "Coogler")),
        "synopsis": "Dos jóvenes reconstruyen el mapa perdido de su barrio antes de una mudanza.",
    },
    {
        "title": "Bosque de luciérnagas",
        "year": 2019,
        "duration": 96,
        "director": ("Hayao", "Miyazaki"),
        "genres": ("Animación", "Aventura"),
        "cast": (("Patty", "Jenkins"),),
        "synopsis": "Una niña sigue una constelación de luciérnagas para devolver la lluvia al valle.",
    },
    {
        "title": "Gravedad cero",
        "year": 2023,
        "duration": 131,
        "director": ("Alfonso", "Cuarón"),
        "genres": ("Ciencia ficción", "Drama"),
        "cast": (("Greta", "Gerwig"), ("Denis", "Villeneuve")),
        "synopsis": "Una ingeniera orbital debe regresar a la Tierra después de perder comunicación.",
    },
    {
        "title": "La ruta del jaguar",
        "year": 2022,
        "duration": 112,
        "director": ("Ryan", "Coogler"),
        "genres": ("Aventura", "Drama"),
        "cast": (("Alfonso", "Cuarón"),),
        "synopsis": "Una expedición comunitaria protege una reserva durante una temporada de incendios.",
    },
    {
        "title": "Órbita interior",
        "year": 2018,
        "duration": 125,
        "director": ("Christopher", "Nolan"),
        "genres": ("Ciencia ficción",),
        "cast": (("Denis", "Villeneuve"), ("Patty", "Jenkins")),
        "synopsis": "Un físico descubre que sus recuerdos siguen el patrón de una órbita imposible.",
    },
    {
        "title": "Voces del andén",
        "year": 2017,
        "duration": 101,
        "director": ("Céline", "Sciamma"),
        "genres": ("Drama",),
        "cast": (("Greta", "Gerwig"), ("Alfonso", "Cuarón")),
        "synopsis": "Historias de cuatro viajeros coinciden durante el cierre de una estación.",
    },
    {
        "title": "La casa que camina",
        "year": 2016,
        "duration": 109,
        "director": ("Hayao", "Miyazaki"),
        "genres": ("Animación", "Aventura"),
        "cast": (("Ryan", "Coogler"),),
        "synopsis": "Una vivienda mecánica recorre las montañas buscando a su antigua familia.",
    },
    {
        "title": "Marea roja",
        "year": 2024,
        "duration": 116,
        "director": ("Patty", "Jenkins"),
        "genres": ("Drama", "Ciencia ficción"),
        "cast": (("Christopher", "Nolan"), ("Céline", "Sciamma")),
        "synopsis": "Una bióloga marina investiga un fenómeno que altera la memoria de una ciudad costera.",
    },
]


class Command(BaseCommand):
    help = "Create demo users, editor permissions, and reproducible sample data."

    def add_arguments(self, parser):
        parser.add_argument("--skip-data", action="store_true")
        parser.add_argument("--skip-users", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["skip_users"]:
            self._configure_users_and_permissions()
        if not options["skip_data"]:
            self._load_sample_data()

    def _configure_users_and_permissions(self):
        group, _ = Group.objects.get_or_create(name="editores")
        permission_names = {
            ("movie", "view_movie"),
            ("movie", "add_movie"),
            ("movie", "change_movie"),
            ("genre", "view_genre"),
            ("person", "view_person"),
            ("rating", "view_rating"),
        }
        permissions = Permission.objects.filter(
            content_type__app_label="movies"
        ).select_related("content_type")
        selected = [
            permission
            for permission in permissions
            if (permission.content_type.model, permission.codename) in permission_names
        ]
        group.permissions.set(selected)

        user_model = get_user_model()
        admin_user, _ = user_model.objects.get_or_create(
            username="admin_lab",
            defaults={"email": "admin@example.local"},
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_password = os.environ.get("LAB_ADMIN_PASSWORD")
        if admin_password:
            admin_user.set_password(admin_password)
        elif not admin_user.has_usable_password():
            admin_user.set_unusable_password()
        admin_user.save()

        editor_user, _ = user_model.objects.get_or_create(
            username="editor_lab",
            defaults={"email": "editor@example.local"},
        )
        editor_user.is_staff = True
        editor_user.is_superuser = False
        editor_user.user_permissions.clear()
        editor_password = os.environ.get("LAB_EDITOR_PASSWORD")
        if editor_password:
            editor_user.set_password(editor_password)
        elif not editor_user.has_usable_password():
            editor_user.set_unusable_password()
        editor_user.save()
        editor_user.groups.set([group])

        self.stdout.write(
            self.style.SUCCESS(
                "Usuarios admin_lab y editor_lab configurados; grupo editores actualizado."
            )
        )

    def _load_sample_data(self):
        genres = {
            name: Genre.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )[0]
            for name, description in GENRES.items()
        }
        people = {
            (first_name, last_name): Person.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
            )[0]
            for first_name, last_name in PEOPLE
        }

        for index, data in enumerate(MOVIES, start=1):
            movie, _ = Movie.objects.update_or_create(
                title=data["title"],
                release_year=data["year"],
                defaults={
                    "duration_minutes": data["duration"],
                    "director": people[data["director"]],
                    "synopsis": data["synopsis"],
                },
            )
            movie.genres.set(genres[name] for name in data["genres"])
            movie.cast.set(people[name] for name in data["cast"])
            Rating.objects.update_or_create(
                movie=movie,
                reviewer_name="Comité del laboratorio",
                defaults={
                    "score": 3 + (index % 3),
                    "comment": "Valoración de prueba para verificar promedios y recomendaciones.",
                },
            )
            if index <= 5:
                Rating.objects.update_or_create(
                    movie=movie,
                    reviewer_name="Club de cine",
                    defaults={
                        "score": 4 + (index % 2),
                        "comment": "Segunda valoración para comprobar el bloque en línea.",
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos cargados: 4 géneros, 8 personas, 10 películas y 15 valoraciones."
            )
        )

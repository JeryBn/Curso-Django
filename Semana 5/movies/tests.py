from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .admin import GenreAdmin, MovieAdmin, PersonAdmin, RatingAdmin, RatingInline
from .models import Genre, Movie, Person, Rating


class CatalogTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.science_fiction = Genre.objects.create(name="Ciencia ficción")
        cls.drama = Genre.objects.create(name="Drama")
        cls.director = Person.objects.create(first_name="Ana", last_name="Torres")
        cls.selected_movie = Movie.objects.create(
            title="Órbita de prueba",
            synopsis="Película usada como origen de las recomendaciones.",
            release_year=2024,
            duration_minutes=120,
            director=cls.director,
        )
        cls.selected_movie.genres.add(cls.science_fiction)
        cls.best_match = Movie.objects.create(
            title="Mejor coincidencia",
            synopsis="Comparte género y tiene la valoración más alta.",
            release_year=2023,
            duration_minutes=110,
            director=cls.director,
        )
        cls.best_match.genres.add(cls.science_fiction)
        cls.second_match = Movie.objects.create(
            title="Segunda coincidencia",
            synopsis="Comparte género con un promedio menor.",
            release_year=2022,
            duration_minutes=105,
            director=cls.director,
        )
        cls.second_match.genres.add(cls.science_fiction)
        cls.other_genre = Movie.objects.create(
            title="Drama independiente",
            synopsis="No comparte género con la selección.",
            release_year=2021,
            duration_minutes=95,
            director=cls.director,
        )
        cls.other_genre.genres.add(cls.drama)
        Rating.objects.create(
            movie=cls.best_match,
            reviewer_name="Crítico A",
            score=5,
        )
        Rating.objects.create(
            movie=cls.second_match,
            reviewer_name="Crítico B",
            score=3,
        )
        Rating.objects.create(
            movie=cls.other_genre,
            reviewer_name="Crítico C",
            score=5,
        )


class ModelTests(CatalogTestMixin, TestCase):
    def test_string_representations_are_descriptive(self):
        rating = Rating.objects.get(movie=self.best_match)

        self.assertEqual(str(self.science_fiction), "Ciencia ficción")
        self.assertEqual(str(self.director), "Ana Torres")
        self.assertEqual(str(self.selected_movie), "Órbita de prueba (2024)")
        self.assertIn("Mejor coincidencia: 5/5", str(rating))

    def test_movie_title_and_year_are_unique_together(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Movie.objects.create(
                title=self.selected_movie.title,
                synopsis="Duplicado",
                release_year=self.selected_movie.release_year,
                duration_minutes=90,
                director=self.director,
            )

    def test_rating_is_unique_per_reviewer_and_movie(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Rating.objects.create(
                movie=self.best_match,
                reviewer_name="Crítico A",
                score=4,
            )


class AdminConfigurationTests(CatalogTestMixin, TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="admin_test",
            password="temporary-test-password",
        )
        self.client.force_login(self.superuser)

    def test_all_models_use_custom_model_admin_classes(self):
        self.assertIsInstance(admin.site._registry[Genre], GenreAdmin)
        self.assertIsInstance(admin.site._registry[Movie], MovieAdmin)
        self.assertIsInstance(admin.site._registry[Person], PersonAdmin)
        self.assertIsInstance(admin.site._registry[Rating], RatingAdmin)

    def test_movie_admin_has_filters_search_columns_and_inline(self):
        movie_admin = admin.site._registry[Movie]

        self.assertIn("genres", movie_admin.list_filter)
        self.assertIn("release_year", movie_admin.list_filter)
        self.assertIn("title", movie_admin.search_fields)
        self.assertIn("average_rating", movie_admin.list_display)
        self.assertIn(RatingInline, movie_admin.inlines)

    def test_audit_fields_are_read_only_in_every_admin(self):
        for model in (Genre, Movie, Person, Rating):
            model_admin = admin.site._registry[model]
            self.assertIn("created_at", model_admin.readonly_fields)
            self.assertIn("updated_at", model_admin.readonly_fields)

    def test_movie_search_returns_the_matching_title(self):
        response = self.client.get(reverse("admin:movies_movie_changelist"), {"q": "Órbita"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Órbita de prueba")
        self.assertNotContains(response, "Drama independiente")

    def test_movie_year_filter_limits_the_changelist(self):
        response = self.client.get(
            reverse("admin:movies_movie_changelist"),
            {"release_year": "2024"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Órbita de prueba")
        self.assertNotContains(response, "Mejor coincidencia")

    def test_movie_change_form_contains_rating_inline_and_read_only_audit(self):
        response = self.client.get(
            reverse("admin:movies_movie_change", args=[self.selected_movie.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ratings-TOTAL_FORMS")
        self.assertContains(response, "Fecha de creación")
        self.assertNotContains(response, 'name="created_at"')
        self.assertNotContains(response, 'name="updated_at"')


class PermissionTests(CatalogTestMixin, TestCase):
    def setUp(self):
        call_command("setup_lab", "--skip-data", verbosity=0)
        self.editor = get_user_model().objects.get(username="editor_lab")
        self.client.force_login(self.editor)

    def test_editor_has_add_and_change_but_not_delete_movie_permission(self):
        self.assertTrue(self.editor.has_perm("movies.view_movie"))
        self.assertTrue(self.editor.has_perm("movies.add_movie"))
        self.assertTrue(self.editor.has_perm("movies.change_movie"))
        self.assertFalse(self.editor.has_perm("movies.delete_movie"))

    def test_editor_admin_index_hides_user_and_group_management(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Películas")
        self.assertNotContains(response, "Usuarios")
        self.assertNotContains(response, "Grupos")

    def test_editor_cannot_open_movie_delete_page(self):
        response = self.client.get(
            reverse("admin:movies_movie_delete", args=[self.selected_movie.pk])
        )

        self.assertEqual(response.status_code, 403)


class RecommendationViewTests(CatalogTestMixin, TestCase):
    def test_catalog_lists_all_movies_with_rating_annotations(self):
        response = self.client.get(reverse("movies:movie_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Películas disponibles")
        self.assertContains(response, "Mejor coincidencia")

    def test_recommendations_use_same_genre_and_highest_average_first(self):
        response = self.client.get(
            reverse("movies:movie_recommendations", args=[self.selected_movie.pk])
        )
        recommendations = list(response.context["recommendations"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(recommendations, [self.best_match, self.second_match])
        self.assertNotIn(self.selected_movie, recommendations)
        self.assertNotIn(self.other_genre, recommendations)

    def test_unrated_movies_are_not_recommended(self):
        unrated = Movie.objects.create(
            title="Sin valoración",
            synopsis="Comparte género, pero todavía no tiene puntuación.",
            release_year=2020,
            duration_minutes=90,
            director=self.director,
        )
        unrated.genres.add(self.science_fiction)

        response = self.client.get(
            reverse("movies:movie_recommendations", args=[self.selected_movie.pk])
        )

        self.assertNotIn(unrated, list(response.context["recommendations"]))

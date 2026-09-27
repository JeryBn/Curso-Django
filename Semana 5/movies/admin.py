from django.contrib import admin
from django.db.models import Avg, Count

from .models import Genre, Movie, Person, Rating


admin.site.site_header = "Administración de películas"
admin.site.site_title = "Panel de películas"
admin.site.index_title = "Gestión del catálogo"


class AuditFieldsAdminMixin:
    readonly_fields = ("created_at", "updated_at")


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1
    fields = ("reviewer_name", "score", "comment", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(Genre)
class GenreAdmin(AuditFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "movie_count", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    ordering = ("name",)

    @admin.display(description="Películas", ordering="_movie_count")
    def movie_count(self, obj):
        return obj._movie_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_movie_count=Count("movies"))


@admin.register(Person)
class PersonAdmin(AuditFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("full_name", "birth_date", "directed_movie_count", "updated_at")
    list_filter = ("birth_date", "created_at")
    search_fields = ("first_name", "last_name", "biography")
    ordering = ("last_name", "first_name")
    fieldsets = (
        ("Datos personales", {"fields": (("first_name", "last_name"), "birth_date", "photo")}),
        ("Perfil", {"fields": ("biography",)}),
        ("Auditoría", {"fields": (("created_at", "updated_at"),), "classes": ("collapse",)}),
    )

    @admin.display(description="Nombre", ordering="last_name")
    def full_name(self, obj):
        return str(obj)

    @admin.display(description="Películas dirigidas", ordering="_directed_movie_count")
    def directed_movie_count(self, obj):
        return obj._directed_movie_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _directed_movie_count=Count("directed_movies")
        )


@admin.register(Movie)
class MovieAdmin(AuditFieldsAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "release_year",
        "genre_list",
        "director",
        "average_rating",
        "rating_count",
        "updated_at",
    )
    list_filter = ("genres", "release_year")
    search_fields = (
        "title",
        "synopsis",
        "director__first_name",
        "director__last_name",
        "genres__name",
    )
    filter_horizontal = ("genres", "cast")
    autocomplete_fields = ("director",)
    list_select_related = ("director",)
    list_per_page = 20
    inlines = (RatingInline,)
    fieldsets = (
        ("Identificación", {"fields": ("title", ("release_year", "duration_minutes"), "poster")}),
        ("Contenido", {"fields": ("synopsis", "director", "genres", "cast")}),
        ("Auditoría", {"fields": (("created_at", "updated_at"),), "classes": ("collapse",)}),
    )

    @admin.display(description="Géneros")
    def genre_list(self, obj):
        return ", ".join(genre.name for genre in obj.genres.all())

    @admin.display(description="Promedio", ordering="_average_rating")
    def average_rating(self, obj):
        if obj._average_rating is None:
            return "Sin valorar"
        return f"{obj._average_rating:.1f}/5"

    @admin.display(description="Valoraciones", ordering="_rating_count")
    def rating_count(self, obj):
        return obj._rating_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("genres")
            .annotate(
                _average_rating=Avg("ratings__score"),
                _rating_count=Count("ratings", distinct=True),
            )
        )


@admin.register(Rating)
class RatingAdmin(AuditFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("movie", "reviewer_name", "score", "created_at", "updated_at")
    list_filter = ("score", "movie__genres", "created_at")
    search_fields = ("movie__title", "reviewer_name", "comment")
    autocomplete_fields = ("movie",)
    list_select_related = ("movie",)
    ordering = ("-created_at",)

from django.urls import path

from . import views


app_name = "movies"

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path(
        "peliculas/<int:pk>/recomendaciones/",
        views.movie_recommendations,
        name="movie_recommendations",
    ),
]

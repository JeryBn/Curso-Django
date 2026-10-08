from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import Movie


def movie_list(request):
    movies = (
        Movie.objects.select_related("director")
        .prefetch_related("genres")
        .annotate(
            average_rating=Avg("ratings__score"),
            rating_count=Count("ratings", distinct=True),
        )
        .order_by("title")
    )
    return render(request, "movies/movie_list.html", {"movies": movies})


def movie_recommendations(request, pk):
    selected_movie = get_object_or_404(
        Movie.objects.select_related("director").prefetch_related("genres"),
        pk=pk,
    )
    recommendations = (
        Movie.objects.select_related("director")
        .prefetch_related("genres")
        .annotate(
            average_rating=Avg("ratings__score"),
            rating_count=Count("ratings", distinct=True),
        )
        .filter(genres__in=selected_movie.genres.all(), rating_count__gt=0)
        .exclude(pk=selected_movie.pk)
        .distinct()
        .order_by("-average_rating", "title")[:6]
    )
    return render(
        request,
        "movies/recommendations.html",
        {
            "selected_movie": selected_movie,
            "recommendations": recommendations,
        },
    )

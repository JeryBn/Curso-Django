from django.urls import path

from .views import BookDetailView, BookListView

app_name = "library"

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
]

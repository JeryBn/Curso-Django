from django.db.models import Prefetch, Q
from django.views.generic import DetailView, ListView

from .forms import BookFilterForm
from .models import Author, Book, Category, Publication, Publisher


class BookListView(ListView):
    model = Book
    template_name = "library/book_list.html"
    context_object_name = "books"
    paginate_by = 8

    def get_queryset(self):
        self.filter_form = BookFilterForm(self.request.GET)
        queryset = Book.objects.select_related("author").prefetch_related(
            "categories"
        )
        if not self.filter_form.is_valid():
            return queryset.none()

        query = self.filter_form.cleaned_data["q"]
        category = self.filter_form.cleaned_data["category"]
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(author__first_name__icontains=query)
                | Q(author__last_name__icontains=query)
                | Q(isbn__icontains=query)
            )
        if category:
            queryset = queryset.filter(categories=category)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context.update(
            {
                "filter_form": self.filter_form,
                "query_string": query_params.urlencode(),
                "book_count": Book.objects.count(),
                "author_count": Author.objects.count(),
                "category_count": Category.objects.count(),
                "publisher_count": Publisher.objects.count(),
            }
        )
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = "library/book_detail.html"
    context_object_name = "book"
    queryset = Book.objects.select_related("author__profile").prefetch_related(
        "categories",
        Prefetch(
            "publications",
            queryset=Publication.objects.select_related("publisher"),
        ),
    )

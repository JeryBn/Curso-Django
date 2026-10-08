from django.shortcuts import get_object_or_404, render
from .models import Article, Category


def portal_context():
    return {"categories": Category.objects.all()}


def home(request):
    articles = (
        Article.objects.published()
        .select_related("author")
        .prefetch_related("categories")
    )
    return render(request, "news/home.html", {**portal_context(), "articles": articles})


def detail(request, slug):
    article = get_object_or_404(
        Article.objects.published()
        .select_related("author")
        .prefetch_related("categories"),
        slug=slug,
    )
    return render(request, "news/detail.html", {**portal_context(), "article": article})


def category(request, slug):
    selected_category = get_object_or_404(Category, slug=slug)
    articles = (
        Article.objects.published()
        .filter(categories=selected_category)
        .select_related("author")
        .prefetch_related("categories")
    )
    return render(
        request,
        "news/category.html",
        {
            **portal_context(),
            "selected_category": selected_category,
            "articles": articles,
        },
    )

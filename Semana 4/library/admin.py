from django.contrib import admin

from .models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)


class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    extra = 1
    max_num = 1


class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 1
    autocomplete_fields = ["book", "publisher"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email"]
    search_fields = ["first_name", "last_name", "email"]
    inlines = [AuthorProfileInline]


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ["author", "country", "birth_date"]
    list_filter = ["country"]
    search_fields = ["author__first_name", "author__last_name", "biography"]
    autocomplete_fields = ["author"]
    list_select_related = ["author"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "website"]
    list_filter = ["country"]
    search_fields = ["name"]
    inlines = [PublicationInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "isbn"]
    list_filter = ["categories", "author", "publishers"]
    search_fields = ["title", "isbn", "author__last_name"]
    autocomplete_fields = ["author"]
    filter_horizontal = ["categories"]
    list_select_related = ["author"]
    inlines = [PublicationInline]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ["book", "publisher", "publication_date", "edition"]
    list_filter = ["publisher", "publication_date"]
    search_fields = ["book__title", "publisher__name"]
    autocomplete_fields = ["book", "publisher"]
    list_select_related = ["book", "publisher"]

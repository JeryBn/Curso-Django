from django.contrib import admin
from .models import Article, Author, Category

admin.site.site_header = "Administración de Actualidad Digital"
admin.site.site_title = "Panel del portal"
admin.site.index_title = "Gestión de noticias y catálogo"


class AuditAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(AuditAdmin):
    list_display = ("name", "slug", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Author)
class AuthorAdmin(AuditAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "biography")


@admin.register(Article)
class ArticleAdmin(AuditAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "categories", "author", "published_at")
    search_fields = ("title", "summary", "body", "author__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    date_hierarchy = "published_at"
    list_select_related = ("author",)

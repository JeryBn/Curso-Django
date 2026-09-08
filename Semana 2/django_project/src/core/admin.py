from django.contrib import admin

from .models import Item


# Register the Item model in the admin site.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # Fields displayed in the admin list view.
    list_display = ("name", "created_at")
    # Fields available for search in the admin.
    search_fields = ("name",)

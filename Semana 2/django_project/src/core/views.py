from django.shortcuts import render

from .models import Item


# Display the list of all items.
def item_list(request):
    # Retrieve all items from the database.
    items = Item.objects.all()
    # Render the list template with the items in the context.
    return render(request, "core/item_list.html", {"items": items})

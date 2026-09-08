from django.db import models


# Item represents a simple catalog entry.
class Item(models.Model):
    # Short name of the item.
    name = models.CharField(max_length=120)
    # Optional long description of the item.
    description = models.TextField(blank=True)
    # Timestamp set automatically when the item is created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Return the item name as its string representation.
    def __str__(self):
        return self.name

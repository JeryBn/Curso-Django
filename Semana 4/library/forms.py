from django import forms

from .models import Category


class BookFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=120,
        label="Buscar un libro",
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": "Título, autor o ISBN…",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Categoría",
        empty_label="Todas las categorías",
    )

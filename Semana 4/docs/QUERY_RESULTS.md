# Consultas y resultados registrados

Registro técnico obtenido el **11 de septiembre de 2026**, con Python 3.14.7,
Django 5.2.17 y SQLite. La base de ejemplo se cargó mediante `seed_library`.
Los resultados corresponden a ese conjunto; cambiarán al editar sus datos.

## 1. Cantidades iniciales

```text
Sample data is ready.
Author: 2
AuthorProfile: 2
Book: 4
Category: 3
Publisher: 2
Publication: 5
```

## 2. Consultas de ida, vuelta y filtrado

Reproducir con:

```powershell
$env:PYTHONUTF8 = "1"
.\.venv\Scripts\python.exe manage.py inspect_relations
```

Para escribirlas manualmente en `manage.py shell`, importa los modelos y
`connection`, y prepara estas variables:

```python
from django.db import connection
from library.models import Book, Category, Publisher

book = Book.objects.get(isbn="9780307474728")
author = book.author
category = Category.objects.get(name="Realismo mágico")
publisher = Publisher.objects.get(name="Editorial Horizonte")
```

### ForeignKey: libro → autor y autor → libros

```pycon
>>> str(book.author)
'Gabriel García Márquez'
>>> list(author.books.values_list("title", flat=True))
['Cien años de soledad', 'El amor en los tiempos del cólera']
```

El primer acceso retorna un autor. El segundo consulta los libros que
referencian su identificador mediante el `related_name="books"`.

### OneToOneField: autor → perfil y perfil → autor

```pycon
>>> author.profile.country
'Colombia'
>>> str(author.profile.author)
'Gabriel García Márquez'
```

### ManyToManyField: libro ↔ categoría

```pycon
>>> list(book.categories.values_list("name", flat=True))
['Novela', 'Realismo mágico']
>>> list(category.books.values_list("title", flat=True))
['Cien años de soledad', 'La casa de los espíritus']
```

Un libro aparece en varias categorías y la categoría consultada reúne
libros de distintos autores.

### ManyToManyField con through: libro ↔ editorial

```pycon
>>> list(book.publishers.distinct().values_list("name", flat=True))
['Editorial Horizonte', 'Editorial Sur']
>>> list(publisher.books.distinct().values_list("title", flat=True))
['Cien años de soledad', 'La casa de los espíritus', 'Largo pétalo de mar']
```

### Datos propios del intermedio, desde ambos lados

```pycon
>>> list(book.publications.values_list("publisher__name", "publication_date", "edition"))
[('Editorial Horizonte', datetime.date(2024, 6, 1), 2), ('Editorial Sur', datetime.date(2020, 5, 15), 1)]
>>> list(publisher.publications.values_list("book__title", "publication_date", "edition"))
[('Cien años de soledad', datetime.date(2024, 6, 1), 2), ('La casa de los espíritus', datetime.date(2022, 8, 2), 1), ('Largo pétalo de mar', datetime.date(2023, 4, 20), 1)]
```

La fecha y la edición se recuperan desde `Publication` y también se muestran
en el detalle. El orden proviene de `Publication.Meta.ordering`.

### Filtros con doble guion bajo

```pycon
>>> list(Book.objects.filter(author__last_name="García Márquez").values_list("title", flat=True))
['Cien años de soledad', 'El amor en los tiempos del cólera']
>>> list(Book.objects.filter(categories__name="Realismo mágico").distinct().values_list("title", flat=True))
['Cien años de soledad', 'La casa de los espíritus']
>>> list(Book.objects.filter(publications__edition__gte=2).distinct().values_list("title", flat=True))
['Cien años de soledad']
```

### Tablas creadas

```pycon
>>> [name for name in connection.introspection.table_names() if name.startswith("library_")]
['library_author', 'library_authorprofile', 'library_book', 'library_book_categories', 'library_category', 'library_publication', 'library_publisher']
```

Se verificaron las seis tablas de modelos y la intermedia implícita de
categorías. `Publication` es la intermedia explícita para editoriales.

## 3. Borrado real durante el desarrollo

Se ejecutó `author.delete()` sobre Gabriel García Márquez con los modelos
activos de cada etapa. El orden de los contadores es:
**autores, libros, perfiles, publicaciones**.

### Etapa inicial: CASCADE

```text
Book.author.on_delete = CASCADE
Before: 2 4 2 5
Deletion: (11, {'library.Book_categories': 4, 'library.Publication': 3, 'library.AuthorProfile': 1, 'library.Book': 2, 'library.Author': 1})
After: 1 2 1 2
Categories and publishers: 3 2
Rollback: 2 4 2 5
```

Se eliminaron once filas en total. Las categorías y editoriales permanecieron.
La transacción restauró los datos de ejemplo al terminar el experimento.

### Etapa final: PROTECT

Después de cambiar el campo, generar `0002_protect_book_author` y aplicar
la migración:

```text
Book.author.on_delete = PROTECT
ProtectedError - protected books: 2
After: 2 4 2 5
```

El ORM bloqueó la operación completa, incluido el borrado del perfil.

## 4. Comparación automatizada con modelos históricos

Resultado real de `python manage.py compare_deletions`. Cada etapa usa
un conjunto temporal de un autor y un libro, por eso sus contadores
difieren del experimento anterior sobre Gabriel.

```text
CASCADE (library.0001_initial)
Deleted rows: 5
Remaining: Author=0, AuthorProfile=0, Book=0, Publication=0, Category=1, Publisher=1, Book_categories=0
Temporary data rolled back.
PROTECT (library.0002_protect_book_author)
ProtectedError: 1 book(s) prevent deletion.
Remaining: Author=1, AuthorProfile=1, Book=1, Publication=1, Category=1, Publisher=1, Book_categories=1
Temporary data rolled back.
```

Una prueba compara todos los registros de las siete tablas antes y después
del comando y verifica que las transacciones los conserven.

## 5. Verificaciones realizadas

```text
Found 29 test(s).
System check identified no issues (0 silenced).
Ran 29 tests
OK
```

El análisis de código con `ruff check .` devolvió `All checks passed!`.
También se comprobó que catálogo y detalle respondieran HTTP 200, que el
detalle mostrara la editorial y su fecha, y que el CSS se encontrara.
Las capturas se obtuvieron en Chromium sobre la aplicación ejecutándose.

Comprobaciones adicionales:

- `manage.py check`: sin incidencias.
- `makemigrations --check --dry-run`: `No changes detected`.
- `showmigrations library`: las migraciones `0001` y `0002` están aplicadas.
- `pip check`: `No broken requirements found`.
- Navegador: búsqueda por Isabel, filtro por Realismo mágico y limpieza
  de filtros, con 2, 1 y 4 libros respectivamente.
- Catálogo y detalle sin desbordamiento horizontal en anchos de 320, 390,
  640, 641, 768, 800, 801, 960 y 1440 píxeles.
- Navegación desde el detalle hasta el formulario de acceso al administrador.

| Grupo | Casos | Comprobaciones principales |
|---|---:|---|
| Relaciones | 13 | Ida/vuelta, uno a uno, muchos a muchos, políticas de borrado, ISBN y restricciones de edición. |
| Catálogo y detalle | 8 | Búsqueda, filtros inválidos, paginación, datos opcionales, escape HTML, 404 y tres consultas para el detalle. |
| Administrador | 3 | Alta de libro con imagen, categoría y publicación; alta de autor con perfil; borrado protegido. |
| Comandos y esquema | 5 | Semilla repetible, consultas, datos faltantes, comparación histórica y tablas intermedias. |

Los resultados automáticos complementan las capturas personales que exige
el documento del curso; esas capturas deben añadirse al entregable.

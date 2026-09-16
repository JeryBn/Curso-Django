# Guía de desarrollo · Laboratorio 4

Esta guía sigue los doce pasos del documento del curso. Los archivos completos
están en `Semana 4`; para ejecutarlos, comienza por el [README](../README.md).

## 1. Crear el proyecto e instalar dependencias

El esqueleto de Django se crea con estos comandos en una carpeta vacía y con
las dependencias instaladas:

```powershell
.\.venv\Scripts\python.exe -m django startproject config .
.\.venv\Scripts\python.exe manage.py startapp library
```

En este repositorio el esqueleto ya está desarrollado. `requirements.txt`
declara Django, Pillow y `python-dotenv`. En `config/settings.py` se registra:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "library.apps.LibraryConfig",
]
```

`manage.py` ejecuta comandos; `config` configura el proyecto y `library`
concentra la responsabilidad de la biblioteca.

## 2. Configurar medios

En `config/settings.py`:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

En `config/urls.py` se añade `static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)` cuando `DEBUG` está activo. Esto permite
ver las imágenes subidas durante el desarrollo. Los estilos se sirven desde
`library/static/library/css/styles.css` mediante `django.contrib.staticfiles`.

`Book.cover` guarda portadas y `AuthorProfile.photo` guarda fotografías. Pillow
permite validar las imágenes en los formularios del administrador.

## 3. Declarar los modelos

Consulta [library/models.py](../library/models.py). Los modelos principales
son `Author`, `Book`, `Publisher` y `Category`. Se añaden `AuthorProfile` y
`Publication` para representar sus datos relacionados.

Cada modelo tiene campos propios, `Meta` y `__str__`. La ordenación definida
en `Meta` hace que el administrador y las consultas tengan un orden estable.

## 4. Relacionar un libro con su autor

La versión inicial utilizó `CASCADE`. La versión final queda así:

```python
author = models.ForeignKey(
    Author,
    on_delete=models.PROTECT,
    related_name="books",
)
```

`book.author` obtiene un objeto; `author.books.all()` obtiene varios libros.
La base guarda `author_id` en cada fila de `library_book`.

## 5. Separar el perfil biográfico

```python
author = models.OneToOneField(
    Author,
    on_delete=models.CASCADE,
    related_name="profile",
)
```

Está declarado en `AuthorProfile`. Los recorridos son `author.profile` y
`profile.author`. La restricción única evita asignar dos perfiles a un autor.

## 6. Crear los muchos a muchos

En `Book`:

```python
categories = models.ManyToManyField(
    Category, related_name="books", blank=True
)
publishers = models.ManyToManyField(
    Publisher,
    through="Publication",
    related_name="books",
    blank=True,
)
```

`Publication` tiene `book`, `publisher`, `publication_date` y `edition`.
La fecha y la edición pertenecen a esa publicación concreta. En el admin,
las categorías se seleccionan con el selector múltiple y las publicaciones
se agregan en las filas del formulario integrado del libro.

## 7. Generar migraciones y comprobar las tablas

Durante el desarrollo se generaron y aplicaron:

1. `0001_initial.py`: modelos completos con `Book.author` en `CASCADE`.
2. `0002_protect_book_author.py`: cambio de ese campo a `PROTECT`.

Comandos habituales después de modificar modelos:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations library
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py showmigrations library
.\.venv\Scripts\python.exe manage.py sqlmigrate library 0001
```

En un clon, `migrate` aplica las migraciones ya incluidas. Para inspeccionar
la base sin instalar un cliente SQLite:

```powershell
.\.venv\Scripts\python.exe manage.py shell
```

```python
from django.db import connection

[
    name
    for name in connection.introspection.table_names()
    if name.startswith("library_")
]
```

El resultado contiene las siete tablas del [diagrama](MODEL_DIAGRAM.md),
incluidas `library_book_categories` y `library_publication`.

## 8. Cargar datos desde el administrador

Inicia `runserver`, entra en <http://127.0.0.1:8000/admin/> y utiliza el
superusuario que creaste. Los modelos tienen nombres en inglés para mantener
la convención del curso.

### A. Autores y perfiles

Abre **Library → Authors → Añadir**. Completa nombre y apellido; en el mismo
formulario completa **Author profile**. El correo, el sitio web y la fotografía
son opcionales.

| `first_name` | `last_name` | `country` del perfil | `birth_date` |
|---|---|---|---|
| Gabriel | García Márquez | Colombia | 1927-03-06 |
| Isabel | Allende | Chile | 1942-08-02 |

Biografías de ejemplo:

- Gabriel: «Escritor colombiano, referente del realismo mágico y ganador del
  Premio Nobel de Literatura en 1982».
- Isabel: «Escritora chilena nacida en Lima. Sus novelas combinan historias
  familiares, memoria y elementos fantásticos».

### B. Categorías y editoriales

En **Categories**, crea `Novela`, `Realismo mágico` y
`Literatura latinoamericana`. La descripción es opcional.

En **Publishers**, crea estos datos ficticios:

| `name` | `country` |
|---|---|
| Editorial Sur | Perú |
| Editorial Horizonte | Chile |

### C. Libros

En **Books → Añadir**, introduce los siguientes datos. `summary` y `cover`
son opcionales; puedes escribir una sinopsis y subir una imagen local.
En el selector de categorías, mueve las categorías elegidas a la columna
de seleccionadas.

| `title` | `isbn` | `author` | `categories` |
|---|---|---|---|
| Cien años de soledad | 9780307474728 | Gabriel García Márquez | Novela; Realismo mágico |
| El amor en los tiempos del cólera | 9780307389732 | Gabriel García Márquez | Novela; Literatura latinoamericana |
| La casa de los espíritus | 9781501117015 | Isabel Allende | Novela; Realismo mágico |
| Largo pétalo de mar | 9780063021797 | Isabel Allende | Novela; Literatura latinoamericana |

### D. Publicaciones

En las filas **Publications** de cada libro, completa editorial, fecha y
edición. También puedes usar **Library → Publications → Añadir** después
de guardar los libros. Las fechas siguientes están expresadas como
`AAAA-MM-DD`; el administrador muestra el formato de fecha de su interfaz.

| Libro | `publisher` | `publication_date` | `edition` |
|---|---|---|---:|
| Cien años de soledad | Editorial Sur | 2020-05-15 | 1 |
| Cien años de soledad | Editorial Horizonte | 2024-06-01 | 2 |
| El amor en los tiempos del cólera | Editorial Sur | 2021-03-10 | 1 |
| La casa de los espíritus | Editorial Horizonte | 2022-08-02 | 1 |
| Largo pétalo de mar | Editorial Horizonte | 2023-04-20 | 1 |

Captura los listados y el formulario de un libro con dos categorías y dos
publicaciones. Si usaste `seed_library`, identifica esa carga como automática
en tus evidencias; la evidencia de alta manual debe corresponder a una acción
real en el administrador.

## 9. Consultar en ambos sentidos

Abre `manage.py shell` e importa:

```python
from library.models import (
    Author, AuthorProfile, Book, Category, Publication, Publisher
)

book = Book.objects.get(isbn="9780307474728")
author = book.author
category = Category.objects.get(name="Realismo mágico")
publisher = Publisher.objects.get(name="Editorial Horizonte")
```

Ejecuta cada expresión y captura su resultado:

```python
book.author
author.books.all()
author.profile
author.profile.author
book.categories.all()
category.books.all()
book.publishers.distinct()
publisher.books.distinct()
book.publications.all()
publisher.publications.all()

Book.objects.filter(author__last_name="García Márquez")
Book.objects.filter(categories__name="Realismo mágico").distinct()
Book.objects.filter(publications__edition__gte=2).distinct()

for publication in book.publications.select_related("publisher"):
    print(
        publication.publisher.name,
        publication.publication_date,
        publication.edition,
    )
```

El doble guion bajo atraviesa relaciones y también introduce comparadores
como `gte` (mayor o igual). `distinct()` evita duplicar libros o editoriales
cuando varias filas relacionadas cumplen un filtro.

En [QUERY_RESULTS.md](QUERY_RESULTS.md) se registran los resultados con
`values_list`, que facilita leer y comparar los valores.

## 10. Comprobar CASCADE y PROTECT

### Comparación reproducible

```powershell
.\.venv\Scripts\python.exe manage.py compare_deletions
```

El comando utiliza `MigrationLoader` para construir los modelos históricos
de `0001_initial` y `0002_protect_book_author`. Cada experimento crea un autor,
perfil, libro, categoría, editorial y publicación temporales; ejecuta
`author.delete()` y luego revierte la transacción.

Ambos estados comparten la misma estructura física: el cambio de `on_delete`
modifica cómo actúa el ORM. El comando no cambia `library/models.py` ni la
política `PROTECT` activa de la aplicación.

### Repetir el cambio explícito en el código

Para reconstruir las dos etapas usando las migraciones incluidas:

1. Detén el servidor y sal de la consola de Django.
2. En **`Book.author`**, cambia `models.PROTECT` por `models.CASCADE`.
3. Ejecuta `.\.venv\Scripts\python.exe manage.py migrate library 0001_initial`.
   Así, código y estado de migración quedan en la primera etapa.
4. Abre una consola nueva y ejecuta el bloque de abajo.
5. Vuelve a dejar **`Book.author`** en `models.PROTECT`.
6. Ejecuta `.\.venv\Scripts\python.exe manage.py migrate library`,
   abre otra consola y repite el mismo bloque.
7. Verifica `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`.

```python
from django.db import transaction
from django.db.models.deletion import ProtectedError
from library.models import Author, AuthorProfile, Book, Publication

print(Book._meta.get_field("author").remote_field.on_delete.__name__)

with transaction.atomic():
    author = Author.objects.get(last_name="García Márquez")
    try:
        print(author.delete())
    except ProtectedError as error:
        print(type(error).__name__, len(error.protected_objects))
    print(
        Author.objects.count(),
        Book.objects.count(),
        AuthorProfile.objects.count(),
        Publication.objects.count(),
    )
    transaction.set_rollback(True)
```

Termina el bloque con una línea vacía en la consola. `set_rollback(True)`
restaura el conjunto de ejemplo al salir del bloque. Volver una migración
atrás por sí solo no modifica la clase importada desde `models.py`: por eso
hay que cambiar el campo y abrir una consola nueva en cada etapa.

| Política | Resultado sobre Gabriel y sus libros |
|---|---|
| `CASCADE` | Se borran 1 autor, 1 perfil, 2 libros, 3 publicaciones y 4 enlaces con categorías. |
| `PROTECT` | `ProtectedError` señala 2 libros protegidos; todos los registros permanecen. |

La aplicación final conserva `PROTECT` para impedir una pérdida accidental
de libros al eliminar un autor.

## 11. Mostrar las relaciones en la plantilla

El flujo es:

```text
config/urls.py
    -> library/urls.py
        -> BookDetailView
            -> library/book_detail.html
```

La plantilla recorre `book.categories.all` y `book.publications.all`; de
cada publicación obtiene `publication.publisher`, `publication_date` y
`edition`. Muestra `book.author` y los campos de `book.author.profile`.

Abre «Cien años de soledad» en el catálogo. Debes ver dos categorías,
dos publicaciones, la biografía del autor y su país. La captura incluida
está en [evidence/book-detail.png](evidence/book-detail.png).

## 12. Preparar la entrega

Completa [DELIVERY_EVIDENCE.md](DELIVERY_EVIDENCE.md) con los integrantes,
sus actividades y sus capturas. Adjunta el diagrama y el registro de consultas.

Desde la raíz del repositorio, revisa los cambios antes de subirlos:

```powershell
git status
git diff
git log --oneline -10
git add -- "Semana 4"
git diff --cached
git commit -m "Add week 4 library model relationships"
git push
```

Estos comandos de publicación los ejecuta el equipo con su cuenta y su
repositorio configurado. Copia la URL final en el entregable y súbelo al
campus virtual junto con las evidencias solicitadas.

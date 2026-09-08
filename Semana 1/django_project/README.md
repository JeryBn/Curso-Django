# Guia 1 - Laboratorio 1: Desarrollo de una aplicacion Web con Django

Proyecto base Django con estructura `src/`, app `core` y modelo `Item`.

## Estructura

```text
django_project/
├── README.md
├── requirements.txt
├── .gitignore
├── venv/
└── src/
    ├── manage.py
    ├── db.sqlite3
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    └── core/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── tests.py
        ├── migrations/
        │   ├── __init__.py
        │   └── 0001_initial.py
        └── templates/
            ├── base.html
            └── core/
                └── item_list.html
```

## Requisitos

- Python 3.14.7
- Django 6.1.1 (ver `requirements.txt`)
- Windows PowerShell 5.1

## Como activar el venv e instalar

Desde `django_project/`:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m django --version
```

Si el entorno no existe, crearlo e instalar:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install Django
.\venv\Scripts\python.exe -m django --version
```

## Como correr migraciones y servidor

Desde `django_project/src/`:

```powershell
..\venv\Scripts\python.exe manage.py makemigrations
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py createsuperuser --noinput --username admin --email admin@example.com
..\venv\Scripts\python.exe manage.py runserver
```

Abrir `http://127.0.0.1:8000/` en el navegador.

Superusuario de laboratorio:

- user: `admin`
- email: `admin@example.com`
- pass: `admin123`

## Tabla de URLs

| URL | Vista / Descripcion |
|-----|---------------------|
| `/` | `core.views.item_list` (nombre `core:item_list`). Listado de todos los `Item`. |
| `/admin/` | Sitio de administracion de Django. Modelo `Item` registrado. |
| `/admin/login/` | Login del admin (verificacion de acceso). |

La pagina principal `/` usa la plantilla `core/item_list.html` que extiende `base.html` y recorre `items` con `{% for %}` y caso `{% empty %}` ("No hay items").

## Observaciones propias

1. Decision de estructura `src/config/core`: se usa carpeta `src/` para separar el codigo fuente (`manage.py`, `config/`, `core/`) de los archivos de entorno y documentacion (`venv/`, `requirements.txt`, `README.md`, `.gitignore`) que quedan en la raiz `django_project/`. `config/` contiene solo configuracion del proyecto y `core/` la logica de la app, lo que facilita escalar con mas apps.
2. Venv aislado: todo se instala y ejecuta con `django_project/venv` (`.\venv\Scripts\python.exe -m ...`), sin contaminar el Python global. `requirements.txt` se genero con `pip freeze` desde ese venv.
3. ALLOWED_HOSTS local: se deja en `["127.0.0.1", "localhost", "testserver"]` para desarrollo local y para que el Django test Client (host `testserver`) funcione sin `DisallowedHost`.
4. `db.sqlite3` no versionada: la base de datos local se ignora en `.gitignore` (`db.sqlite3` y `db.sqlite3-journal`) porque es un artefacto generado por `migrate` y por los datos de prueba, no codigo fuente.
5. Internacionalizacion simple: `LANGUAGE_CODE = "es-es"` y `TIME_ZONE = "America/Santiago"` para el laboratorio en Chile, sin agregar dependencias externas.
6. Sin credenciales escritas a mano: se conserva el `SECRET_KEY` generado por defecto por Django para el lab y no se agregan claves ni passwords en `settings.py`.

## Casos de prueba

Datos de prueba creados via shell:

- `Item uno` / `Descripcion del primer item`
- `Item dos` / `Descripcion del segundo item`

Verificaciones realizadas:

1. `python manage.py check` -> `System check identified no issues (0 silenced).`
2. `GET /` con Django test Client -> `200` y el contenido incluye `Item uno` e `Item dos`.
3. `GET /admin/login/` con Django test Client -> `200`.
4. Archivo de migracion verificado en `src/core/migrations/0001_initial.py`.
5. `git check-ignore -v venv db.sqlite3` confirma que ambos estan ignorados por `.gitignore`.

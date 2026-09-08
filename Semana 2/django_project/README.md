# Guia 2 - Laboratorio 2: Flujo de trabajo en Django

App `tasks` con datos estaticos en memoria (sin base de datos), sobre la base acumulativa del Lab 1 (`core` con `Item`).

## Decision importante: version estatica (rubrica por sobre procedimiento)

El procedimiento de la guia pide `Task` con base de datos, `ModelForm` y 5 vistas CRUD con filtrado,
pero la **rubrica criterio 2 exige expresamente NO usar base de datos** (datos estaticos en el modulo
de modelos, `Form` simple no `ModelForm`, solo listar + crear, sin editar/eliminar/filtrado) y penaliza
con `Regular` si se resuelve con BD. Para optar al 20/20 se implementa la **version estatica de la rubrica**:
`src/tasks/models.py` sin clases Django (lista `TASKS` + funciones), `src/tasks/forms.py` con
`forms.Form`, y solo dos vistas (`task_list` y `task_create`).

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
    ├── core/               # Base acumulativa del Lab 1 (Item con BD)
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── tests.py
    │   ├── migrations/
    │   │   ├── __init__.py
    │   │   └── 0001_initial.py
    │   └── templates/
    │       ├── base.html
    │       └── core/
    │           └── item_list.html
    └── tasks/              # Nueva app estatica (sin BD)
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py       # Lista TASKS + get_tasks/get_task_by_id/add_task
        ├── forms.py        # TaskForm (forms.Form)
        ├── views.py        # task_list + task_create
        ├── urls.py         # app_name tasks
        ├── tests.py
        ├── migrations/
        │   └── __init__.py
        └── templates/
            └── tasks/
                ├── task_list.html
                └── task_form.html
```

## Requisitos

- Python 3.14.7
- Django 6.1.1 (ver `requirements.txt`)
- Windows PowerShell 5.1

## Instalacion

Desde `django_project/`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m django --version
```

## Como correr migraciones y servidor

Desde `django_project/src/`:

```powershell
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py createsuperuser --noinput --username admin --email admin@example.com
..\venv\Scripts\python.exe manage.py runserver
```

Abrir `http://127.0.0.1:8000/` en el navegador. La variable `DJANGO_SUPERUSER_PASSWORD` debe estar
definida al crear el superusuario (valor de laboratorio: `admin123`).

Superusuario de laboratorio:

- user: `admin`
- email: `admin@example.com`
- pass: `admin123`

## Tabla de URLs

| URL | Vista / Descripcion |
|-----|---------------------|
| `/` | `core.views.item_list` (nombre `core:item_list`). Listado acumulativo de `Item` del Lab 1. |
| `/tasks/` | `tasks.views.task_list` (nombre `tasks:task_list`). Tabla con las tareas estaticas y `total`. |
| `/tasks/create/` | `tasks.views.task_create` (nombre `tasks:task_create`). GET muestra `TaskForm`, POST valida y redirige a `tasks:task_list`. |
| `/admin/` | Sitio de administracion de Django. Modelo `Item` registrado. |
| `/admin/login/` | Login del admin (verificacion de acceso). |

La app `tasks` reutiliza el `base.html` existente de `core` (`core/templates/base.html`, encontrado por
`APP_DIRS`). No se creo `src/templates/base.html` ni se modifico `TEMPLATES.DIRS` porque no hizo falta.

## Observaciones propias

1. Acumulativo desde Lab 1: se copio `src/config`, `src/core` (archivos `.py`, templates y migraciones)
   y `src/manage.py` desde `Semana 1/django_project/src` tal cual, sin copiar `venv` ni `db.sqlite3`.
   La BD se regenero con `migrate` y los `Item` de prueba se recrearon. `INSTALLED_APPS` y `config/urls.py`
   mantienen `core` intacto y agregan `tasks`.
2. Decision estatica (rubrica criterio 2): se implemento sin base de datos para `tasks` porque la rubrica
   lo exige y penaliza con `Regular` el uso de BD. `models.py` no tiene clases Django, solo la lista
   `TASKS` y funciones. No hay migraciones para `tasks` (solo existen las de `core`/`admin`/`auth`).
3. `Form` vs `ModelForm`: se usa `forms.Form` (`TaskForm`) con `title`, `description`, `status`
   (`pending`/`in_progress`/`done`) y `priority` (`low`/`medium`/`high`), con validacion estandar de Django
   via `is_valid()` y `cleaned_data`. No corresponde `ModelForm` porque no hay modelo de BD.
4. Contexto con nombres claros y sin globales: `task_list` pasa `{"tasks": ..., "total": ...}` y
   `task_create` pasa `{"form": ...}`. Las plantillas solo reciben datos por ese contexto (`tasks`, `total`,
   `form`, mas `messages` del context processor).
5. Tres tareas iniciales con prioridades distintas: `Prepare lab report` (`high`/`pending`),
   `Review Django forms` (`medium`/`in_progress`) y `Organize project files` (`low`/`done`), con campos en
   ingles `title`, `description`, `status`, `priority` y `created_at` como string (`2026-09-01/02/03`).
   Las nuevas tareas reciben `id` correlativo y `created_at = "2026-09-08"`.
6. `settings` de laboratorio: `ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]` (incluye
   `testserver` para el Django test Client), `LANGUAGE_CODE = "es-es"` y `TIME_ZONE = "America/Santiago"`.
7. Datos en memoria: las tareas creadas por POST viven solo en el proceso (`TASKS`). Al reiniciar el
   servidor vuelve a las 3 iniciales. Es el comportamiento esperado de la version estatica.

## Casos de prueba

Datos de prueba:

- `core`: `Item uno` / `Descripcion del primer item`, `Item dos` / `Descripcion del segundo item`.
- `tasks`: las 3 tareas iniciales de `TASKS` + `Nueva tarea de prueba` creada por POST en la verificacion.

Verificaciones realizadas con Django test `Client` (todas PASS):

1. `GET /` -> `200` y contiene `Item uno` e `Item dos` (acumulativo intacto).
2. `GET /tasks/` -> `200` y contiene `Prepare lab report`, `Review Django forms` y `Organize project files`.
3. `POST /tasks/create/` valido (`title=Nueva tarea de prueba`, `status=pending`, `priority=high`) -> `302` a `/tasks/`.
4. `GET /tasks/` siguiente -> `200` y contiene `Nueva tarea de prueba`.
5. `GET /admin/login/` -> `200`.
6. `python manage.py check` -> `System check identified no issues (0 silenced).`

## Anadir un campo nuevo a la tarea (archivos a tocar, en orden)

1. `src/tasks/models.py`: agregar la clave al dict de las 3 tareas iniciales de `TASKS` y al dict que
   construye `add_task()`, porque es la unica "fuente de verdad" estatica. Si el campo debe pedirse en el
   formulario, agregar el parametro correspondiente a `add_task()`.
2. `src/tasks/forms.py`: agregar el campo al `TaskForm` (tipo y `choices` si aplica), porque la validacion
   estandar de Django ocurre aqui antes de guardar en memoria.
3. `src/tasks/views.py`: pasar el nuevo valor desde `form.cleaned_data` hacia `add_task()` en `task_create`,
   porque la vista es el puente entre formulario y almacenamiento. En `task_list` no hay cambio salvo que se
   quiera exponer un derivado (por ejemplo un conteo) con un nombre claro en el contexto.
4. `src/tasks/templates/tasks/task_form.html`: mostrar el campo (ya sale automatico con `{{ form.as_p }}`,
   pero ajustar etiquetas/ayudas si se quiere), porque es la interfaz de carga.
5. `src/tasks/templates/tasks/task_list.html`: agregar la columna al `<table>` (`<th>` y `<td>`) para
   visualizarlo, porque el listado solo muestra lo que la plantilla recorre desde `tasks`.
6. `src/tasks/urls.py` y `src/config/urls.py`: solo si el campo exige una nueva pagina o filtro con ruta
   propia (por ejemplo `/tasks/<prioridad>/`). Para un campo simple de alta/listado no se tocan, las rutas
   `""` y `"create/"` ya cubren listar y crear.

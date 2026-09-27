# GLAB-S05: Administración avanzada con Django

Proyecto académico que implementa un catálogo de películas para practicar relaciones entre modelos, personalización de `ModelAdmin`, administración de usuarios y grupos, permisos diferenciados y una vista pública de recomendaciones.

## Resultado implementado

El sistema contiene cuatro modelos relacionados:

- `Genre`: clasifica las películas y se relaciona con ellas mediante muchos a muchos.
- `Person`: representa directores y miembros del reparto.
- `Movie`: pertenece a un director, admite varios géneros y varias personas en el reparto.
- `Rating`: pertenece a una película y almacena una puntuación de 1 a 5.

Todos los modelos heredan campos de auditoría `created_at` y `updated_at`. En el administrador estos campos son de solo lectura.

El panel de administración incluye:

- columnas útiles en cada listado;
- filtros por género, año, puntuación y fechas;
- búsqueda por título, nombres, sinopsis y comentarios;
- selección cómoda para relaciones muchos a muchos;
- valoraciones editables dentro de la película mediante `TabularInline`;
- promedios y cantidad de valoraciones calculados en el listado;
- nombres, títulos y etiquetas en español.

La vista pública permite consultar las diez películas de demostración y solicitar recomendaciones. Las recomendaciones comparten al menos un género con la película seleccionada, excluyen la propia película y las obras sin valoración, y se ordenan por el promedio más alto.

## Estructura principal

```text
config/                         Configuración y rutas generales
movies/
  admin.py                      ModelAdmin e inline de valoraciones
  models.py                     Modelos y relaciones
  views.py                      Catálogo y recomendaciones
  urls.py                       Rutas públicas
  tests.py                      Pruebas automatizadas
  management/commands/
    setup_lab.py                Usuarios, permisos y datos reproducibles
templates/                      Plantillas HTML
static/movies/site.css          Diseño de la vista pública
evidencias/                     Capturas verificadas
manage.py                       Punto de entrada de Django
```

## Requisitos

- Python 3.12 o compatible.
- Django 5.2.17.
- Pillow 12.3.0.

Las versiones exactas están en `requirements.txt`.

## Instalación desde cero en Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
```

Para crear el grupo, los usuarios de demostración y la información del catálogo, define contraseñas temporales en la sesión actual y ejecuta el comando. Las contraseñas no se guardan en el repositorio.

```powershell
$env:LAB_ADMIN_PASSWORD = "Escribe-una-clave-segura"
$env:LAB_EDITOR_PASSWORD = "Escribe-otra-clave-segura"
.\.venv\Scripts\python.exe manage.py setup_lab
Remove-Item Env:LAB_ADMIN_PASSWORD
Remove-Item Env:LAB_EDITOR_PASSWORD
```

También se puede cambiar una contraseña local sin modificar el código:

```powershell
.\.venv\Scripts\python.exe manage.py changepassword admin_lab
.\.venv\Scripts\python.exe manage.py changepassword editor_lab
```

## Ejecución

Se puede hacer doble clic en `INICIAR-LABORATORIO.ps1` o ejecutar:

```powershell
.\INICIAR-LABORATORIO.ps1
```

El laboratorio usa el puerto **8095**:

- Catálogo: `http://127.0.0.1:8095/`
- Administrador: `http://127.0.0.1:8095/admin/`

## Usuarios y permisos

El comando `setup_lab` crea estos usuarios locales:

| Usuario | Rol | Alcance |
|---|---|---|
| `admin_lab` | Superusuario | Administración completa, incluidos usuarios, grupos y permisos |
| `editor_lab` | Miembro de `editores` | Puede ver, agregar y modificar películas; no puede eliminarlas ni administrar cuentas |

El grupo `editores` recibe exactamente estos permisos:

- ver, agregar y modificar películas;
- ver géneros;
- ver personas;
- ver valoraciones;
- sin permiso para eliminar películas;
- sin acceso a usuarios ni grupos.

## Datos de demostración

El comando reproduce:

- 4 géneros;
- 8 personas;
- 10 películas;
- 15 valoraciones;
- valoraciones en al menos 5 películas, tal como pide la guía.

Durante la elaboración, estos datos también se cargaron y revisaron directamente desde el panel para obtener evidencia real del flujo CRUD.

## Pruebas y verificaciones

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test -v 2
```

La ejecución final verificó 15 pruebas. Cubren restricciones de los modelos, registro de todos los `ModelAdmin`, columnas, filtros, búsqueda, valoraciones en línea, auditoría de solo lectura, permisos del editor y el orden de las recomendaciones.

## Evidencias

La carpeta `evidencias` conserva capturas con nombres numerados. La guía resuelta incorpora las capturas principales y explica qué valida cada una. El archivo `EVIDENCIAS.md` sirve como índice técnico y relaciona cada imagen con un requisito.

## Publicación en el repositorio del equipo

El proyecto queda preparado como repositorio Git local. Para subirlo hace falta la dirección exacta del repositorio del equipo y una cuenta autorizada. Cuando esa información esté disponible:

```powershell
git remote add origin URL_DEL_REPOSITORIO_DEL_EQUIPO
git push -u origin main
```

No se incluyeron contraseñas, tokens, archivos `.env` ni otras credenciales.

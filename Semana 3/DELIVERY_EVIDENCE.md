# Evidencia de entrega — Quiz

## Responsables y desarrollo

| Dato | Completar por el equipo |
| --- | --- |
| Autor responsable | `[nombre y apellido]` |
| Correo institucional o identificador | `[dato no secreto]` |
| Título del desarrollo | `Quiz: gestión de exámenes, preguntas y opciones` |
| Fecha de validación | `[AAAA-MM-DD]` |
| Entorno validado | `[SO, Python y Django]` |

**Resultado observable:** se pueden listar y consultar exámenes; cada examen muestra sus preguntas y opciones. Desde la aplicación se crea una pregunta con cuatro opciones y la validación exige exactamente una correcta. El administrador permite cargar un examen, dos preguntas y cuatro opciones por pregunta.

## Modelo de datos y justificación de campos

### `Exam`

| Atributo | Tipo | Justificación |
| --- | --- | --- |
| `title` | `CharField(max_length=200)` | Un título es texto breve con límite explícito y validación natural de formulario. |
| `description` | `TextField(blank=True)` | Permite una explicación de longitud variable y admite que el examen no la necesite. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Conserva automáticamente la fecha de creación para ordenar sin intervención del usuario. |

`Meta` ordena por creación descendente y título; sus nombres administrativos son *examen/exámenes*. `__str__` devuelve `title`.

### `Question`

| Atributo | Tipo | Justificación |
| --- | --- | --- |
| `exam` | `ForeignKey(Exam, CASCADE, related_name="questions")` | Una pregunta pertenece a un examen; al borrar este no deben quedar preguntas huérfanas y el nombre inverso es legible. |
| `prompt` | `TextField()` | El enunciado puede ser más largo que un título y es obligatorio. |
| `score` | `PositiveIntegerField(default=1)` | La puntuación no admite negativos y el valor inicial mantiene compatibilidad con preguntas existentes. |

`Meta` ordena por clave primaria y usa *pregunta/preguntas*. `__str__` devuelve `prompt`.

### `Choice`

| Atributo | Tipo | Justificación |
| --- | --- | --- |
| `question` | `ForeignKey(Question, CASCADE, related_name="choices")` | Cada opción depende de una pregunta y se elimina con ella; facilita `question.choices`. |
| `text` | `CharField(max_length=255)` | La opción es texto breve con longitud máxima controlada. |
| `is_correct` | `BooleanField(default=False)` | Representa inequívocamente dos estados y empieza como incorrecta para evitar marcar respuestas por defecto. |

`Meta` ordena por clave primaria y usa *opción/opciones*. `__str__` devuelve `text`.

## Migraciones verificadas

- `0001_initial`: tres operaciones `CreateModel`: `Exam`, `Question` y `Choice`; incluye sus campos, `Meta`, claves foráneas, `CASCADE` y los `related_name`.
- `0002_question_score`: depende de `("quiz", "0001_initial")` y contiene una única operación `AddField` sobre `question`: `score = PositiveIntegerField(default=1)`. El valor por defecto permite aplicar la migración cuando ya hay filas.

## Código relevante y casos cubiertos

| Objetivo | Código relevante | Pruebas |
| --- | --- | --- |
| Modelos, relaciones, `Meta` y texto | `src/quiz/models.py` | representaciones, orden, nombres, relaciones inversas y borrado en cascada |
| Migraciones y esquema | `src/quiz/migrations/0001_initial.py`, `0002_question_score.py` | operaciones declaradas, dependencia, tablas y columna `quiz_question.score` |
| Una única respuesta correcta | `src/quiz/forms.py` | formset con cero, dos y una opción correcta |
| Listado, detalle y alta | `src/quiz/views.py`, `src/quiz/templates/quiz/` | HTTP 200/redirección, contexto, contenido y persistencia de cuatro opciones |
| Administración | `src/quiz/admin.py` | registro de los tres modelos y carga de un examen con dos preguntas y cuatro opciones cada una |

## Comandos reproducibles y resultado esperado

Defina localmente `DJANGO_SECRET_KEY` con un valor de desarrollo no compartido antes de ejecutar los comandos. No incluya esa clave en este informe.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py showmigrations quiz
.\.venv\Scripts\python.exe manage.py migrate --plan
.\.venv\Scripts\python.exe manage.py test quiz -v 2
.\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; expected={'quiz_exam','quiz_question','quiz_choice'}; print({name: [column.name for column in connection.introspection.get_table_description(connection.cursor(), name)] for name in expected if name in connection.introspection.table_names()})"
```

Registrar aquí la salida de la ejecución final del equipo:

| Comando | Resultado observado | Evidencia (archivo/enlace interno) |
| --- | --- | --- |
| `check` | Ejecutado el 2026-09-04: `System check identified no issues (0 silenced).` | `[adjuntar captura/registro]` |
| `makemigrations --check --dry-run` | Ejecutado el 2026-09-04: `No changes detected`. | `[adjuntar captura/registro]` |
| `showmigrations quiz` | Ejecutado el 2026-09-04: `[X] 0001_initial`, `[X] 0002_question_score`. | `[adjuntar captura/registro]` |
| `migrate --plan` | Ejecutado el 2026-09-04: `No planned migration operations.` | `[adjuntar captura/registro]` |
| `test quiz -v 2` | Ejecutado el 2026-09-04: 15 pruebas ejecutadas, `OK`. | `[adjuntar captura/registro]` |
| Inspección de esquema | Ejecutado el 2026-09-04: existen `quiz_exam`, `quiz_question`, `quiz_choice`; `quiz_question` incluye `score`. | `[adjuntar captura/registro]` |

## Capturas y verificación manual pendientes

No se han tomado capturas como parte de este archivo. El equipo debe capturar, sin mostrar contraseñas, tokens ni claves:

1. **Estructura del editor:** explorador abierto en `src/quiz/`, mostrando `models.py`, `forms.py`, `views.py`, `admin.py`, `migrations/0001_initial.py`, `migrations/0002_question_score.py` y `tests.py`.
2. **Formulario de alta de pregunta:** una captura de la validación con cero o más de una opción correcta y otra con exactamente una correcta antes de guardar.
3. **Resultado público:** detalle de un examen con una pregunta, cuatro opciones y la opción correcta visible.
4. **Administración:** `/admin/` mostrando el examen creado, sus dos preguntas y cuatro opciones por pregunta. Ocultar datos personales si aparecen.
5. **Consola:** salida completa de `check`, `showmigrations quiz`, `migrate --plan`, pruebas e inspección de esquema.

### Datos manuales de administración

| Dato | Valor a completar por el equipo |
| --- | --- |
| URL de administración | `[por ejemplo, http://127.0.0.1:8000/admin/]` |
| Usuario superusuario creado manualmente | `[identificador; no contraseña]` |
| Fecha/hora de creación | `[AAAA-MM-DD HH:MM zona]` |
| Examen de evidencia | `[título]` |
| Preguntas cargadas | `[dos enunciados]` |

Crear el superusuario manualmente con `python manage.py createsuperuser`; no registrar aquí la contraseña ni ningún secreto.

# Django semana 8

API de cuestionarios y laboratorio extra de contrato OpenAPI, cliente de consola y frontera del agente.

Alumno: Jery Becerra Ninaquispe. Sección A.

## Origen y solución

Base docente: [Hellscythe25/dae-s08-api-headless](https://github.com/Hellscythe25/dae-s08-api-headless), revisión `5bdd1fac96c114d1b6e190f1e7994ad564f4d145`. Las instrucciones originales se conservan en `README_DOCENTE.md`.

Se completaron `exit_code_for`, `build_question_payload` y `AgentPermission`. Para cubrir la guía base se añadió el recurso `choices`, sus reglas de integridad y la API navegable con autenticación de sesión. Se añadieron diez pruebas del recurso de opciones y dos de la API navegable. La pasarela y las pruebas originales del docente se conservan.

## Ejecutar en Windows

Se necesita Python 3.12 o superior compatible con las versiones del archivo de dependencias.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python manage.py migrate
python manage.py seed_quiz
python manage.py runserver 127.0.0.1:8000
```

`seed_quiz` reemplaza los cuestionarios locales con los datos didácticos y muestra los tokens de `profe` y `agente`. Úsalo en una base local de prácticas. Los tokens se generan en cada instalación y no se incluyen en esta entrega. Para entrar con contraseña en la API navegable, establece una contraseña local con `python manage.py changepassword profe` y abre `/api-auth/login/`.

La aplicación está configurada para desarrollo local. Las capturas se verificaron con el mismo proyecto en el puerto 8089; el puerto 8000 de estas instrucciones es intercambiable.

## Rutas

| Recurso | Colección | Detalle |
|---|---|---|
| Exámenes | `/api/exams/` | `/api/exams/{id}/` |
| Preguntas | `/api/questions/` | `/api/questions/{id}/` |
| Opciones | `/api/choices/` | `/api/choices/{id}/` |

La raíz navegable está en `/api/`, Swagger UI en `/api/docs/` y OpenAPI en `/api/schema/`. `openapi.yml` contiene el contrato generado. Las colecciones usan GET y POST; los detalles admiten GET, PUT, PATCH y DELETE según el rol. Una pregunta contiene al menos dos opciones y exactamente una correcta. Las escrituras sobre opciones independientes también deben conservar esta regla; no se permite trasladarlas a otra pregunta.

Filtro y búsqueda: `/api/questions/?exam=1&search=ORM`. Paginación: `/api/questions/?page=2`, con cinco registros por página.

## Cliente de consola

En otra terminal, configura los tokens que mostró tu instalación:

```powershell
$env:QUIZ_URL = "http://127.0.0.1:8000"
$env:QUIZ_TOKEN_HUMANO = "TOKEN_LOCAL_DE_PROFE"
$env:QUIZ_TOKEN_AGENTE = "TOKEN_LOCAL_DE_AGENTE"
$env:QUIZ_TOKEN = $env:QUIZ_TOKEN_HUMANO
python quizctl.py --json exams list
python quizctl.py --json questions list --search ORM
python quizctl.py --json questions create --exam 1 --text "¿Qué es REST?" --choice "Un estilo:ok" --choice "Un lenguaje"
python quizctl.py --dry-run questions delete 1
python quizctl.py ops
```

`--json` y `--dry-run` van antes del subcomando. El sufijo final `:ok` marca la opción correcta. El servidor valida el número de opciones correctas. Códigos de salida: 0 éxito; 1 uso u otro error; 2 validación; 3 autenticación o permisos; 4 no encontrado; 5 error del servidor; 6 conexión.

## Permisos y pasarela

El usuario con `is_staff` puede realizar todas las operaciones conocidas. El grupo `agente` puede leer, crear y modificar; nunca eliminar. Los demás usuarios autenticados solo pueden leer. Los métodos desconocidos se rechazan.

La pasarela acepta intenciones escritas a mano y una lista cerrada de operaciones declaradas en OpenAPI. R0 permite lectura; R1 permite creación con el token del agente; R2 solicita un plan con hash y el token de la persona antes de borrar. Las respuestas se marcan como `untrusted_data`, de modo que el texto hostil del fixture se conserva como datos. No hace falta conectar un modelo para resolver las pruebas del laboratorio.

## Verificación

```powershell
python manage.py check
python manage.py test
python manage.py spectacular --file openapi.yml --validate
```

Resultado: **73 pruebas satisfactorias**, sin incidencias del sistema. También pasaron **32 comprobaciones HTTP, 6 casos de consola y 6 controles de pasarela** contra el servidor local. Los registros sin credenciales están en `verification/`.

La guía Word situada en la carpeta superior contiene las capturas del funcionamiento, el código en imágenes, los casos de prueba, la tabla de la API y las conclusiones dentro del mismo documento.

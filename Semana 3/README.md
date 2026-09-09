# Semana 3 - Creación de modelos en Django

**Autor:** Jery Becerra Ninaquispe

**Sección:** 4.º A

**Modalidad:** trabajo individual

Este proyecto implementa un sistema básico de exámenes en Django. Un examen contiene preguntas y cada pregunta contiene opciones de respuesta. La aplicación permite listar y consultar exámenes, crear preguntas desde un formulario y administrar los tres modelos desde el panel de Django.

## Contenido del laboratorio

- `Exam`: título, descripción y fecha de creación.
- `Question`: enunciado, examen asociado, orden y puntaje.
- `Choice`: texto, indicador de respuesta correcta, pregunta asociada y orden.
- Migraciones versionadas en `quiz/migrations/`.
- Formularios y un formset para registrar una pregunta junto con sus opciones.
- Vistas y plantillas para el listado, detalle y creación de registros.
- Registro administrativo de exámenes, preguntas y opciones.

La evidencia complementaria del laboratorio está en [DELIVERY_EVIDENCE.md](DELIVERY_EVIDENCE.md).

## Requisitos

- Python 3.12 o superior.
- Las dependencias indicadas en `requirements.txt`.

## Instalación y ejecución

Desde la carpeta `Semana 3`, crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Luego abre [http://127.0.0.1:8000/examenes/](http://127.0.0.1:8000/examenes/) en el navegador.

- Panel de administración: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Inicio de sesión: [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)

Usa `Ctrl+C` en la terminal para detener el servidor.

## Uso esperado

1. Crea un examen desde el administrador.
2. Registra dos preguntas para el examen.
3. Añade cuatro opciones a cada pregunta y marca una como correcta.
4. Abre el detalle del examen para comprobar que se muestren las preguntas y sus opciones.

Al crear una pregunta mediante el formulario, se muestran cuatro opciones. La validación del conjunto exige que se marque exactamente una respuesta correcta.

## Verificación

Antes de entregar, ejecuta los siguientes comandos:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py showmigrations quiz
```

No se deben versionar el entorno virtual, la base de datos local, contraseñas, claves ni archivos de configuración privados.

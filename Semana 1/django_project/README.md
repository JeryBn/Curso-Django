# Laboratorio 1 Desarrollo de una aplicación web con Django

Primera etapa del proyecto acumulativo del curso. Esta carpeta corresponde únicamente a la semana 1. La semana 2 partirá de esta versión y conservará su propia carpeta de entrega.

## Entorno

Se creó un entorno virtual local llamado `venv` con Python 3.13.15 y se instaló Django 5.2.17. Las versiones exactas de las dependencias se generaron ejecutando `python -m pip freeze`; están en `requirements.txt`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m django --version
python -m pip check
```

El entorno virtual, la base de datos local, las credenciales y los archivos generados de Python están excluidos mediante `.gitignore`. Cada persona debe crear su entorno virtual después de clonar el repositorio.

## Avance

Primera etapa completada: entorno aislado, dependencias verificadas y estructura inicial `src/config` generada con Django. Los siguientes commits incorporarán la aplicación `core`, el modelo, las migraciones, las vistas, las plantillas y sus comprobaciones.

## Observaciones del entorno

- Python estaba instalado en el equipo, pero no estaba disponible en el PATH de la terminal de trabajo. Se utilizó la ruta del ejecutable instalado para crear el entorno.
- `python -m pip check` terminó sin dependencias incompatibles.
- `venv` es una carpeta local: no se sube a GitHub. `requirements.txt` permite reproducir las dependencias.

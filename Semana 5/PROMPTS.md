# Registro de asistencia utilizada

Este laboratorio se desarrolló con asistencia de inteligencia artificial solicitada por el estudiante. La asistencia se usó para interpretar la guía, preparar la estructura del proyecto, implementar modelos y relaciones, configurar el administrador, diseñar pruebas, verificar permisos, organizar evidencias y completar la documentación.

## Solicitud principal

> Resolver el laboratorio según la guía, trabajar en el equipo local, documentar lo elaborado y presentar evidencias del funcionamiento y del proceso de desarrollo.

## Decisiones revisables por el estudiante

- Se utilizó Django 5.2 con SQLite para conservar un entorno local sencillo y reproducible.
- El servidor se configuró en el puerto 8095.
- Se añadieron restricciones de integridad para evitar películas duplicadas por título y año y valoraciones duplicadas del mismo crítico.
- Los campos de auditoría se centralizaron en un modelo abstracto.
- Los permisos del grupo `editores` se limitaron deliberadamente para demostrar la diferencia frente al superusuario.
- Se incluyó una vista pública de recomendaciones basada en género compartido y promedio de puntuaciones.

El estudiante debe revisar el código, ejecutar las pruebas y comprender cada decisión antes de presentar o modificar la entrega.

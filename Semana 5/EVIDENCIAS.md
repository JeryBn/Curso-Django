# Índice de evidencias — GLAB-S05

Fecha de verificación: 26 de septiembre de 2026.

## Estado final verificado

| Componente | Resultado |
|---|---|
| Comprobación de Django | Sin problemas detectados |
| Migraciones pendientes | Ninguna |
| Pruebas automatizadas | 15 aprobadas |
| Géneros | 4 |
| Personas | 8 |
| Películas | 10 |
| Valoraciones | 15 |
| Grupo `editores` | Configurado |
| Eliminación de películas por editor | Denegada |
| Recomendaciones | Mismo género, con valoración y mayor promedio primero |

## Relación de capturas

1. `01_admin_registro_basico.jpg`: registro inicial de los cuatro modelos; demuestra el administrador funcional antes de la personalización avanzada.
2. `02_admin_personalizado_listado.jpg`: listado de diez películas con columnas de género, director, promedio, cantidad de valoraciones y fecha de modificación, además de filtros laterales.
3. `03_admin_busqueda_titulo.jpg`: búsqueda por título en el `ModelAdmin` de películas.
4. `04_admin_inline_auditoria_detalle.jpg`: formulario de película con campos de auditoría de solo lectura y valoraciones administradas en línea.
5. `05_grupo_editores_permisos.jpg`: grupo `editores` con permisos seleccionados; se observa agregar/cambiar/ver películas y la ausencia de eliminación.
6. `06_editor_panel_restringido.jpg`: panel visto como `editor_lab`; no aparecen usuarios ni grupos y las entidades auxiliares se muestran en modo de consulta.
7. `07_editor_listado_sin_eliminar.jpg`: listado accesible para el editor sin acción de eliminación.
8. `08_catalogo_publico.jpg`: catálogo público con diez películas, géneros, director, promedio y enlace a recomendaciones.
9. `09_recomendaciones_mismo_genero.jpg`: resultado público ordenado por valoración para películas del mismo género.

## Cobertura de las pruebas automatizadas

- representación legible de cada modelo;
- unicidad de película por título y año;
- unicidad de valoración por crítico y película;
- registro de los cuatro `ModelAdmin`;
- filtros, búsqueda, columnas e inline de `MovieAdmin`;
- campos de auditoría de solo lectura en todos los administradores;
- búsqueda por título y filtro por año;
- restricción real de eliminación para el usuario editor;
- ocultamiento de usuarios y grupos para el editor;
- respuesta del catálogo público;
- selección y orden de recomendaciones;
- exclusión de películas sin valoración.

## Evidencia del proceso de elaboración

La evidencia de elaboración se completa con los archivos fuente `movies/models.py`, `movies/admin.py`, `movies/views.py`, `movies/management/commands/setup_lab.py` y `movies/tests.py`. La guía resuelta incorpora fragmentos comentados de esos archivos y el resultado final de las verificaciones.

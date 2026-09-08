# Evidencias del laboratorio 1

Estas capturas pertenecen al archivo de la guía 1, en una sección denominada Desarrollo, antes de Conclusiones. Cada bloque debe contener nombre del alumno, título, captura, código o comandos, explicación y caso de prueba. Completar el nombre y el reparto de trabajo con datos reales.

| Orden y nombre de imagen | Ubicación en el entregable de la guía 1 | Qué debe verse |
| --- | --- | --- |
| L01-01-entorno.png | Desarrollo 1 Entorno virtual e instalación, pasos 1 y 2 | Consola con `(venv)`, Python, versión de Django, ejecutable dentro de venv y dependencias. |
| L01-02-estructura.png | Desarrollo 2 Estructura y registro de la aplicación, pasos 3 y 4 | VS Code con django_project, src/config, src/core, requirements.txt y .gitignore; settings con core en INSTALLED_APPS. |
| L01-03-modelo-migracion.png | Desarrollo 3 Modelo y migraciones, pasos 5 y 6 | Modelo Item y migración inicial; complementar con salida de migrate y showmigrations. |
| L01-04-rutas-vista.png | Desarrollo 4 Vista, rutas y plantillas, pasos 7 a 9 | item_list, contexto y include de core.urls; plantilla con extends, for y empty. |
| L01-05-admin.png | Desarrollo 5 Registro y carga desde administración, pasos 10 y 11 | URL del admin de Item y dos registros creados. Evitar incluir contraseñas. |
| L01-06-listado.png | Desarrollo 6 Resultado en navegador, paso 11 | URL local completa y listado con los dos items del administrador. |
| L01-07-pruebas.png | Desarrollo 7 Casos de prueba | Resultado de comprobaciones del proyecto y pruebas de listado vacío y con registros. |
| L01-08-entrega.png | Desarrollo 8 Dependencias, observaciones e historial, pasos 12 y 13 | README, requirements generado por pip freeze, .gitignore con contenido e historial de commits del laboratorio 1 en GitHub. Puede dividirse en dos capturas legibles. |

## Primera captura

Título: Creación y verificación del entorno virtual.

Comandos: `python -m venv venv`, activación de `venv`, `python --version`, `python -m django --version`, `python -m pip freeze` y `python -m pip check`.

Explicación: el intérprete y las dependencias pertenecen al entorno local de este proyecto. El archivo requirements registra las versiones instaladas; el entorno se excluye de Git para que cada integrante lo recree.

Caso de prueba: verificar que `sys.prefix != sys.base_prefix` sea verdadero y que `pip check` no informe dependencias incompatibles.

Registrar las capturas solo cuando se haya ejecutado el paso y el resultado esté visible. El resto de los bloques se completará con los resultados comprobados durante el desarrollo.

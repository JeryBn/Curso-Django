# Capturas del laboratorio

Las capturas del catálogo y del detalle se generan sobre la aplicación local
con los datos de ejemplo. No contienen credenciales.

Archivos de referencia:

- `catalog-desktop.png`: catálogo completo en escritorio.
- `book-detail.png`: categorías, perfil del autor y publicaciones de un libro.
- `catalog-mobile.png`: catálogo en pantalla móvil.

Para el entregable, añade las capturas personales del administrador, las
consultas en la consola, la comparación de borrado y la estructura del proyecto
en Visual Studio Code. El formato está en `../DELIVERY_EVIDENCE.md`.

## Reproducir las capturas

Instala las herramientas de desarrollo indicadas en el README del proyecto
y ejecuta `python -m playwright install chromium` con el entorno virtual.
Con el servidor activo en el puerto 8000, desde otra terminal en `Semana 4`:

```powershell
.\.venv\Scripts\python.exe -m playwright screenshot --browser chromium --viewport-size "1440,1050" --full-page http://127.0.0.1:8000/ "docs/evidence/catalog-desktop.png"
.\.venv\Scripts\python.exe -m playwright screenshot --browser chromium --viewport-size "1440,1100" --full-page http://127.0.0.1:8000/books/1/ "docs/evidence/book-detail.png"
.\.venv\Scripts\python.exe -m playwright screenshot --browser chromium --viewport-size "390,844" --full-page http://127.0.0.1:8000/ "docs/evidence/catalog-mobile.png"
```

El identificador `1` corresponde al primer libro de una base nueva cargada
con `seed_library`. Usa la URL del libro correspondiente en tu propia base.

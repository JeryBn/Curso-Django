from pathlib import Path

root=Path(__file__).resolve().parents[1]
seed=root/'news/management/commands/seed_news.py'
text=seed.read_text(encoding='utf-8').replace('Django conecta el contenido con sus plantillas','Django publica cambios desde el administrador')
text=text.replace('            if created:\n                article.categories.set', '''            if created and index == 0:
                article.body = 'El contenido de esta noticia fue modificado desde el administrador de Django y se publica sin editar las plantillas.\\n\\nPrueba de escapado: <strong>Texto importante</strong> y <script>alert("prueba")</script>. Las etiquetas se muestran literalmente y no se ejecutan.'
                article.save()
            if created:
                article.categories.set''')
seed.write_text(text,encoding='utf-8')
(root/'README.md').write_text('''# Semana 6 Motor de plantillas con Django

Alumno responsable: Jery Becerra Ninaquispe.

Portal académico Actualidad Digital. Esta entrega continúa la semana 5: conserva la aplicación movies y agrega news, reutilizando TimeStampedModel. El catálogo previo se encuentra en /peliculas/ y el portal de noticias en /.

## Instalación y ejecución

```powershell
py -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe manage.py migrate
.\\.venv\\Scripts\\python.exe manage.py seed_news
.\\.venv\\Scripts\\python.exe manage.py createsuperuser
.\\INICIAR-LABORATORIO.ps1
```

El portal usa http://127.0.0.1:8096/ y el administrador http://127.0.0.1:8096/admin/. Las contraseñas se introducen localmente y no se publican. seed_news genera seis noticias, tres categorías y las seis imágenes PNG mediante Pillow; no necesita servicios externos. Su ejecución repetida conserva las ediciones existentes. Para recrear los datos del catálogo anterior se puede utilizar setup_lab con --skip-users.

## Plantillas y responsabilidades

- templates/news/base.html: estructura HTML, navegación, CSS y bloques title, content y sidebar.
- templates/news/_article_card.html: tarjeta compartida por portada y categoría.
- templates/news/_sidebar.html: fragmento de categorías reutilizado desde base.
- templates/news/home.html: for, empty y tarjetas de noticias publicadas.
- templates/news/category.html: listado filtrado por categoría y reutilización de tarjetas.
- templates/news/detail.html: noticia, imagen, autor, categorías y cuerpo escapado.
- news/views.py: consultas y selección de noticias publicadas; sin lógica de negocio en HTML.
- news/models.py: Article, Author y Category; autor con ForeignKey y categorías con ManyToManyField.
- news/admin.py: columnas, filtros, búsquedas y auditoría de solo lectura para las tres entidades.

Los enlaces utilizan url con nombres news:home, news:detail y news:category. La tarjeta aplica date y truncatewords; las plantillas utilizan if para imágenes y default para valores opcionales. El cuerpo utiliza linebreaks sin safe ni autoescape off.

## Gestión y observaciones

En el administrador se pueden crear y modificar categorías, autores y noticias. Una noticia se muestra cuando está marcada como publicada y su fecha no está en el futuro. Se comprobó un cambio de título y cuerpo desde el panel y su aparición inmediata en el detalle público.

El texto <strong>Texto importante</strong> y <script>alert("prueba")</script> se muestra literalmente: Django escapa los caracteres HTML antes de convertir los saltos de línea. No se ejecuta JavaScript.

STATICFILES_DIRS contiene static y MEDIA_ROOT contiene media. config/urls.py sirve medios solo durante desarrollo. DEBUG=True y el servidor de desarrollo son para ejecución local; publicar código en GitHub no despliega el sitio en Internet.

## Validación

```powershell
.\\.venv\\Scripts\\python.exe manage.py check
.\\.venv\\Scripts\\python.exe manage.py makemigrations --check --dry-run
.\\.venv\\Scripts\\python.exe manage.py test news movies -v 2
```

25 pruebas aprobadas: 10 del portal y 15 de la base de semana 5. Incluyen herencia, include, resumen recortado, categorías, empty, detalle, borradores, fechas futuras, 404, escapado y publicación de cambios del administrador. Las evidencias se encuentran en evidencias y en la guía Word resuelta.

## Entrega y asistencia

Repositorio: https://github.com/JeryBn/Curso-Django/tree/main/Semana%206

La estructura del repositorio ya utiliza Semana 6 y se conserva ese nombre. La guía integra desarrollo, código, casos de prueba, observaciones, conclusiones e imágenes del funcionamiento. PROMPTS.md registra la asistencia utilizada. La entrega al campus virtual corresponde al alumno.
''',encoding='utf-8')
(root/'PROMPTS.md').write_text('''# Registro de asistencia

Solicitud de Jery Becerra Ninaquispe del 8 de octubre de 2026: resolver GLAB-S06 según la guía y la rúbrica, entregar Word con evidencias y publicar en el repositorio Curso-Django, semana 6.

Se utilizó Codex para interpretar los 13 pasos, implementar news sobre la base de semana 5, ejecutar pruebas, comprobar el navegador, registrar capturas, completar la guía y publicar los archivos. El alumno debe revisar el código y las explicaciones para defender y modificar el trabajo. No se atribuye una elaboración sin asistencia.
''',encoding='utf-8')
(root/'EVIDENCIAS.md').write_text('''# Evidencias de laboratorio 6

Capturas reales del 8 de octubre de 2026, obtenidas del portal local y del editor. Las imágenes 11 a 14 muestran la versión de escritorio; 01 y 07 conservan la vista estrecha. 04 muestra seis noticias en el panel; 05 la edición de título y cuerpo; 08 las tres categorías; 09 el bloque empty temporal con los datos posteriormente restaurados; 10 la estructura y la plantilla en Visual Studio Code. pruebas.txt conserva el resultado de 25 pruebas.

Las capturas se incorporan a la guía Word junto con código, resultados y casos de prueba. La evidencia de GitHub se añade después de verificar la publicación remota.
''',encoding='utf-8')
print('Documentation and reproducible content ready.')

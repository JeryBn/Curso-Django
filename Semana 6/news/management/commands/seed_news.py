from datetime import timedelta
from io import BytesIO
import os
from PIL import Image, ImageDraw
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import Article, Author, Category


class Command(BaseCommand):
    help = "Create reproducible news content and an optional local administrator."

    def handle(self, *args, **options):
        categories = [
            Category.objects.get_or_create(
                slug=slug, defaults={"name": name, "description": description}
            )[0]
            for slug, name, description in [
                (
                    "tecnologia",
                    "Tecnología",
                    "Software, herramientas y transformación digital.",
                ),
                ("ciencia", "Ciencia", "Investigación, aprendizaje e innovación."),
                (
                    "comunidad",
                    "Comunidad",
                    "Proyectos y actividades que conectan a las personas.",
                ),
            ]
        ]
        author, _ = Author.objects.get_or_create(
            name="Redacción Digital",
            defaults={
                "biography": "Equipo editorial de demostración del portal académico."
            },
        )
        titles = [
            "Django publica cambios desde el administrador",
            "La tecnología impulsa nuevos proyectos educativos",
            "Un laboratorio acerca la ciencia a los estudiantes",
            "Aprender investigando fortalece el pensamiento crítico",
            "La comunidad comparte ideas para mejorar su entorno",
            "Un portal de noticias reúne las voces de la comunidad",
        ]
        for index, title in enumerate(titles):
            slug = f"noticia-{index+1}"
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": "Este artículo de demostración presenta una iniciativa que conecta conocimientos, experiencias y nuevas oportunidades. El portal organiza información de manera accesible para que los lectores encuentren contenido útil y actualizado en cada sección.",
                    "body": "El proyecto demuestra cómo los datos guardados en la base de datos se transforman en páginas mediante el motor de plantillas de Django.\n\nLa separación entre modelos, vistas y plantillas facilita el mantenimiento del sitio y la publicación de nuevos contenidos.",
                    "author": author,
                    "is_published": True,
                    "published_at": timezone.now() - timedelta(days=index),
                },
            )
            if created and index == 0:
                article.body = 'El contenido de esta noticia fue modificado desde el administrador de Django y se publica sin editar las plantillas.\n\nPrueba de escapado: <strong>Texto importante</strong> y <script>alert("prueba")</script>. Las etiquetas se muestran literalmente y no se ejecutan.'
                article.save()
            if created:
                article.categories.set([categories[index // 2]])
            if not article.featured_image:
                image = Image.new(
                    "RGB", (1000, 500), ["#176e84", "#4b5e92", "#21806a"][index // 2]
                )
                draw = ImageDraw.Draw(image)
                for step in range(8):
                    draw.rounded_rectangle(
                        (60 + step * 105, 100 + (step % 3) * 35, 145 + step * 105, 370),
                        radius=12,
                        fill=["#6eb8c9", "#8796c6", "#6cba9b"][index // 2],
                    )
                draw.text(
                    (50, 30),
                    f"ACTUALIDAD DIGITAL | {categories[index//2].name.upper()} | {index+1}",
                    fill="white",
                    font_size=28,
                )
                output = BytesIO()
                image.save(output, format="PNG")
                article.featured_image.save(
                    f"news-{index+1}.png", ContentFile(output.getvalue()), save=True
                )
        password = os.environ.get("LAB_ADMIN_PASSWORD")
        if password:
            user, _ = get_user_model().objects.get_or_create(username="admin_lab")
            user.is_staff = user.is_superuser = True
            user.set_password(password)
            user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"News ready: {Article.objects.count()} articles, {Category.objects.count()} categories."
            )
        )

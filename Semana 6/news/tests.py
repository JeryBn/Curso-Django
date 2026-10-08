from datetime import timedelta
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Article, Author, Category


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Test Author")
        cls.category = Category.objects.create(name="Technology", slug="technology")
        cls.article = Article.objects.create(
            title="Template engine",
            slug="template-engine",
            summary="One two three " * 30,
            body='Literal HTML: <strong>important</strong><script>alert("test")</script>',
            author=cls.author,
            is_published=True,
        )
        cls.article.categories.add(cls.category)
        cls.user = get_user_model().objects.create_superuser(
            "testadmin", password="Test-only-password-943!"
        )

    def test_home_inherits_base_and_card(self):
        response = self.client.get(reverse("news:home"))
        self.assertEqual(response.status_code, 200)
        for name in ["news/base.html", "news/_article_card.html", "news/_sidebar.html"]:
            self.assertTemplateUsed(response, name)
        self.assertContains(response, "Template engine")
        self.assertContains(response, "…")

    def test_category_reuses_card_and_filters(self):
        other = Article.objects.create(
            title="Other",
            slug="other",
            summary="Summary",
            body="Body",
            author=self.author,
            is_published=True,
        )
        response = self.client.get(self.category.get_absolute_url())
        self.assertTemplateUsed(response, "news/_article_card.html")
        self.assertContains(response, self.article.title)
        self.assertNotContains(response, other.title)

    def test_empty_home(self):
        Article.objects.update(is_published=False)
        self.assertContains(
            self.client.get(reverse("news:home")), "Aún no hay noticias publicadas"
        )

    def test_empty_category(self):
        self.article.categories.clear()
        self.assertContains(
            self.client.get(self.category.get_absolute_url()),
            "Sin noticias en esta categoría",
        )

    def test_drafts_and_future_articles_are_hidden(self):
        self.article.is_published = False
        self.article.save()
        self.assertEqual(
            self.client.get(self.article.get_absolute_url()).status_code, 404
        )
        self.article.is_published = True
        self.article.published_at = timezone.now() + timedelta(days=1)
        self.article.save()
        self.assertEqual(
            self.client.get(self.article.get_absolute_url()).status_code, 404
        )

    def test_html_is_escaped(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, "&lt;strong&gt;important&lt;/strong&gt;")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("test")</script>')

    def test_detail_displays_author_category_and_date(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, self.author.name)
        self.assertContains(response, self.category.name)
        self.assertContains(
            response, timezone.localtime(self.article.published_at).strftime("%Y")
        )

    def test_admin_configuration_for_three_models(self):
        for model in [Article, Author, Category]:
            model_admin = admin.site._registry[model]
            self.assertTrue(model_admin.list_display)
            self.assertTrue(model_admin.list_filter)
            self.assertTrue(model_admin.search_fields)

    def test_admin_edit_is_visible_without_code_changes(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("admin:news_article_change", args=[self.article.pk]),
            {
                "title": "Updated from admin",
                "slug": self.article.slug,
                "summary": "Updated summary",
                "body": self.article.body,
                "author": self.author.pk,
                "categories": [self.category.pk],
                "is_published": "on",
                "published_at_0": "2026-10-01",
                "published_at_1": "09:00:00",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(reverse("news:home")), "Updated from admin")

    def test_unknown_routes_return_404(self):
        self.assertEqual(
            self.client.get(reverse("news:detail", args=["missing"])).status_code, 404
        )
        self.assertEqual(
            self.client.get(reverse("news:category", args=["missing"])).status_code, 404
        )

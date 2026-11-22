"""The base guide also requires Django REST Framework's browsable API."""
from django.contrib.auth.models import User
from django.test import TestCase

from .helpers import seed


class BrowsableApiTests(TestCase):
    def setUp(self):
        seed()
        self.person = User.objects.get(username="profe")
        self.client.force_login(self.person)

    def test_html_root_lists_three_resources(self):
        response = self.client.get("/api/", HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        for resource in ("exams", "questions", "choices"):
            self.assertContains(response, resource)

    def test_html_question_detail_renders_the_forms(self):
        from quiz.models import Question
        question = Question.objects.first()
        response = self.client.get(
            f"/api/questions/{question.pk}/", HTTP_ACCEPT="text/html"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DELETE")
        self.assertContains(response, "PATCH")

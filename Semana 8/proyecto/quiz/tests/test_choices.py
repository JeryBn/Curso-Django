"""The third resource required by the Lab 8 rubric."""
from rest_framework.test import APITestCase

from quiz.models import Choice, Question
from .helpers import exam_id, seed


class ChoiceResourceTests(APITestCase):
    def setUp(self):
        self.person, self.agent = seed()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")
        self.question = Question.objects.first()

    def test_router_exposes_all_three_resources(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"exams", "questions", "choices"})

    def test_choice_crud_over_http(self):
        self.assertEqual(self.client.get("/api/choices/").status_code, 200)
        response = self.client.post("/api/choices/", {
            "question": self.question.pk, "text": "Distractor extra",
            "is_correct": False,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        url = f"/api/choices/{response.json()['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.patch(url, {"text": "Distractor editado"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Distractor editado")
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_missing_question_is_400(self):
        response = self.client.post("/api/choices/", {
            "text": "Sin relación", "is_correct": False,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_second_correct_choice_is_400_and_saves_nothing(self):
        before = Choice.objects.count()
        response = self.client.post("/api/choices/", {
            "question": self.question.pk, "text": "Otra correcta",
            "is_correct": True,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Choice.objects.count(), before)

    def test_cannot_remove_the_only_correct_choice(self):
        choice = self.question.choices.get(is_correct=True)
        self.assertEqual(
            self.client.delete(f"/api/choices/{choice.pk}/").status_code, 400
        )
        self.assertTrue(Choice.objects.filter(pk=choice.pk).exists())

    def test_patch_cannot_leave_zero_correct_choices(self):
        choice = self.question.choices.get(is_correct=True)
        response = self.client.patch(
            f"/api/choices/{choice.pk}/", {"is_correct": False}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        choice.refresh_from_db()
        self.assertTrue(choice.is_correct)

    def test_cannot_move_a_choice_to_another_question(self):
        choice = self.question.choices.first()
        other = Question.objects.exclude(pk=self.question.pk).first()
        response = self.client.patch(
            f"/api/choices/{choice.pk}/", {"question": other.pk}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cannot_leave_less_than_two_choices(self):
        choices = self.question.choices.filter(is_correct=False)
        for choice in list(choices)[:-1]:
            self.assertEqual(
                self.client.delete(f"/api/choices/{choice.pk}/").status_code, 204
            )
        last = self.question.choices.filter(is_correct=False).first()
        self.assertEqual(
            self.client.delete(f"/api/choices/{last.pk}/").status_code, 400
        )

    def test_agent_cannot_delete_choices(self):
        choice = self.question.choices.filter(is_correct=False).first()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.agent}")
        self.assertEqual(
            self.client.delete(f"/api/choices/{choice.pk}/").status_code, 403
        )

    def test_contract_declares_choice_operations(self):
        schema = self.client.get("/api/schema/", {"format": "json"}).json()
        self.assertIn("/api/choices/", schema["paths"])
        self.assertIn("delete", schema["paths"]["/api/choices/{id}/"])

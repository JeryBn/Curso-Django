from importlib import import_module

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import connection, migrations
from django.test import TestCase
from django.urls import reverse

from .forms import ChoiceFormSet
from .models import Choice, Exam, Question


class QuizModelTests(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(title="Python basics", description="Core concepts")
        self.question = Question.objects.create(
            exam=self.exam,
            prompt="Which value is a list?",
            score=3,
        )
        self.choice = Choice.objects.create(
            question=self.question,
            text="[]",
            is_correct=True,
        )

    def test_models_metadata_relationships_and_text_representations(self):
        self.assertEqual(str(self.exam), "Python basics")
        self.assertEqual(str(self.question), "Which value is a list?")
        self.assertEqual(str(self.choice), "[]")
        self.assertEqual(Exam._meta.ordering, ("-created_at", "title"))
        self.assertEqual(Question._meta.ordering, ("pk",))
        self.assertEqual(Choice._meta.ordering, ("pk",))
        self.assertEqual(Exam._meta.verbose_name, "examen")
        self.assertEqual(Question._meta.verbose_name_plural, "preguntas")
        self.assertEqual(Choice._meta.verbose_name_plural, "opciones")
        self.assertEqual(self.question.exam, self.exam)
        self.assertEqual(self.exam.questions.get(), self.question)
        self.assertEqual(self.question.choices.get(), self.choice)
        self.assertEqual(Question._meta.get_field("exam").remote_field.related_name, "questions")
        self.assertEqual(Choice._meta.get_field("question").remote_field.related_name, "choices")
        self.assertEqual(self.question.score, 3)

    def test_deleting_exam_cascades_to_questions_and_choices(self):
        self.exam.delete()

        self.assertFalse(Question.objects.exists())
        self.assertFalse(Choice.objects.exists())


class MigrationDefinitionTests(TestCase):
    def test_initial_migration_creates_the_three_models(self):
        initial_migration = import_module("quiz.migrations.0001_initial").Migration
        created_models = [
            operation.name
            for operation in initial_migration.operations
            if isinstance(operation, migrations.CreateModel)
        ]

        self.assertEqual(created_models, ["Exam", "Question", "Choice"])
        self.assertTrue(initial_migration.initial)

    def test_score_migration_depends_on_initial_and_adds_score(self):
        score_migration = import_module("quiz.migrations.0002_question_score").Migration

        self.assertEqual(score_migration.dependencies, [("quiz", "0001_initial")])
        self.assertEqual(len(score_migration.operations), 1)
        operation = score_migration.operations[0]
        self.assertIsInstance(operation, migrations.AddField)
        self.assertEqual(operation.model_name, "question")
        self.assertEqual(operation.name, "score")
        self.assertEqual(operation.field.default, 1)

    def test_database_has_quiz_tables_and_score_column(self):
        expected_tables = {"quiz_exam", "quiz_question", "quiz_choice"}
        table_names = set(connection.introspection.table_names())

        self.assertTrue(expected_tables.issubset(table_names))
        question_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(), "quiz_question"
            )
        }
        self.assertTrue({"id", "exam_id", "prompt", "score"}.issubset(question_columns))


class ChoiceFormSetTests(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(title="Form validation")
        self.question = Question(exam=self.exam, prompt="Pending question")

    def build_formset(self, correct_indexes):
        data = {
            "choices-TOTAL_FORMS": "4",
            "choices-INITIAL_FORMS": "0",
            "choices-MIN_NUM_FORMS": "0",
            "choices-MAX_NUM_FORMS": "1000",
        }
        for index in range(4):
            data[f"choices-{index}-text"] = f"Option {index + 1}"
            if index in correct_indexes:
                data[f"choices-{index}-is_correct"] = "on"
        return ChoiceFormSet(data=data, instance=self.question, prefix="choices")

    def test_formset_rejects_zero_correct_choices(self):
        formset = self.build_formset(set())

        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())

    def test_formset_rejects_more_than_one_correct_choice(self):
        formset = self.build_formset({0, 1})

        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())

    def test_formset_accepts_exactly_one_correct_choice(self):
        formset = self.build_formset({2})

        self.assertTrue(formset.is_valid())


class QuizViewTests(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(title="HTTP exam", description="View context")
        self.question = Question.objects.create(
            exam=self.exam,
            prompt="Select the correct answer",
            score=2,
        )
        Choice.objects.create(question=self.question, text="Correct", is_correct=True)
        Choice.objects.create(question=self.question, text="Incorrect", is_correct=False)

    def question_post_data(self, correct_indexes):
        data = {
            "prompt": "New question",
            "score": "4",
            "choices-TOTAL_FORMS": "4",
            "choices-INITIAL_FORMS": "0",
            "choices-MIN_NUM_FORMS": "0",
            "choices-MAX_NUM_FORMS": "1000",
        }
        for index in range(4):
            data[f"choices-{index}-text"] = f"New option {index + 1}"
            if index in correct_indexes:
                data[f"choices-{index}-is_correct"] = "on"
        return data

    def test_exam_list_returns_context_and_exam_link(self):
        response = self.client.get(reverse("quiz:exam_list"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["exams"], [self.exam])
        self.assertContains(response, self.exam.title)
        self.assertContains(response, reverse("quiz:exam_detail", args=[self.exam.pk]))

    def test_exam_detail_returns_nested_questions_and_choices(self):
        response = self.client.get(reverse("quiz:exam_detail", args=[self.exam.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["exam"], self.exam)
        self.assertContains(response, self.question.prompt)
        self.assertContains(response, "Correct (correcta)")
        self.assertContains(response, "Incorrect")

    def test_question_create_get_returns_required_context(self):
        response = self.client.get(reverse("quiz:question_create", args=[self.exam.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["exam"], self.exam)
        self.assertIn("form", response.context)
        self.assertIn("formset", response.context)
        self.assertEqual(response.context["formset"].total_form_count(), 4)

    def test_question_create_rejects_invalid_correct_choice_counts(self):
        url = reverse("quiz:question_create", args=[self.exam.pk])
        for correct_indexes in (set(), {0, 1}):
            with self.subTest(correct_indexes=correct_indexes):
                response = self.client.post(url, self.question_post_data(correct_indexes))

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["formset"].non_form_errors())
                self.assertEqual(self.exam.questions.count(), 1)

    def test_question_create_persists_question_and_four_choices(self):
        response = self.client.post(
            reverse("quiz:question_create", args=[self.exam.pk]),
            self.question_post_data({1}),
        )

        self.assertRedirects(response, reverse("quiz:exam_detail", args=[self.exam.pk]))
        created_question = self.exam.questions.get(prompt="New question")
        self.assertEqual(created_question.score, 4)
        self.assertEqual(created_question.choices.count(), 4)
        self.assertEqual(created_question.choices.filter(is_correct=True).count(), 1)


class QuizAdminTests(TestCase):
    def setUp(self):
        admin_user = get_user_model().objects.create_user(
            username="test-admin",
            email="admin@example.test",
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save(update_fields=("is_staff", "is_superuser"))
        self.client.force_login(admin_user)

    def test_all_models_are_registered(self):
        self.assertTrue(admin.site.is_registered(Exam))
        self.assertTrue(admin.site.is_registered(Question))
        self.assertTrue(admin.site.is_registered(Choice))

    def test_admin_can_load_exam_with_two_questions_and_four_choices_each(self):
        exam_response = self.client.post(
            reverse("admin:quiz_exam_add"),
            {"title": "Admin exam", "description": "Created through admin", "_save": "Save"},
        )
        self.assertEqual(exam_response.status_code, 302)
        exam = Exam.objects.get(title="Admin exam")

        for number in range(2):
            question_response = self.client.post(
                reverse("admin:quiz_question_add"),
                {
                    "exam": exam.pk,
                    "prompt": f"Admin question {number + 1}",
                    "score": "1",
                    "_save": "Save",
                },
            )
            self.assertEqual(question_response.status_code, 302)
            question = exam.questions.get(prompt=f"Admin question {number + 1}")
            for option in range(4):
                choice_response = self.client.post(
                    reverse("admin:quiz_choice_add"),
                    {
                        "question": question.pk,
                        "text": f"Question {number + 1} option {option + 1}",
                        "is_correct": "on" if option == 0 else "",
                        "_save": "Save",
                    },
                )
                self.assertEqual(choice_response.status_code, 302)

        self.assertEqual(exam.questions.count(), 2)
        for question in exam.questions.all():
            self.assertEqual(question.choices.count(), 4)
            self.assertEqual(question.choices.filter(is_correct=True).count(), 1)

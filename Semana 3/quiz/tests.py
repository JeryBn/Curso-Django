"""
Step 11 — Comprehensive unit tests for the quiz app.

Covers:
  - Model metadata, relationships, and text representations
  - Migration definitions and database schema
  - Form validation (ExamForm, QuestionForm, ChoiceForm)
  - ChoiceFormSet with zero, exactly one, and multiple correct choices
  - View tests: list, detail, create with validation
  - Admin: registration and exam loading flow (2 questions, 4 choices each)
  - Edge cases: exam with no questions, question with no valid options
"""
from importlib import import_module

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import connection, migrations
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from quiz.forms import (
    ChoiceForm,
    ChoiceFormSet,
    ExamForm,
    QuestionForm,
)
from quiz.models import Choice, Exam, Question


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_user_model = get_user_model()


def _create_admin_user(username="test-admin", password="admin123"):
    user = _user_model.objects.create_user(
        username, "admin@test.com", password
    )
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=("is_staff", "is_superuser"))
    return user


# ---------------------------------------------------------------------------
# 1. Model tests
# ---------------------------------------------------------------------------
class ExamModelTest(TestCase):
    """Tests for the Exam model: fields, str, Meta, cascade."""

    def test_str_returns_titulo(self):
        exam = Exam.objects.create(
            titulo="Final Exam", fecha_creacion="2025-06-01"
        )
        self.assertEqual(str(exam), "Final Exam")

    def test_meta_ordering(self):
        self.assertEqual(Exam._meta.ordering, ["fecha_creacion"])

    def test_meta_verbose_names(self):
        self.assertEqual(Exam._meta.verbose_name, "examen")
        self.assertEqual(Exam._meta.verbose_name_plural, "examenes")

    def test_cascade_deletes_questions(self):
        exam = Exam.objects.create(
            titulo="Cascade Test", fecha_creacion="2025-01-01"
        )
        Question.objects.create(
            examen=exam, enunciado="Q1", orden=1, puntaje=10
        )
        exam.delete()
        self.assertFalse(Question.objects.exists())
        self.assertFalse(Choice.objects.exists())


class QuestionModelTest(TestCase):
    """Tests for the Question model: fields, str, Meta, FK."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="FK Test", fecha_creacion="2025-03-01"
        )

    def test_str_returns_enunciado(self):
        q = Question.objects.create(
            examen=self.exam, enunciado="What is 2+2?", orden=1, puntaje=5
        )
        self.assertEqual(str(q), "What is 2+2?")

    def test_meta_ordering(self):
        self.assertEqual(Question._meta.ordering, ["orden"])

    def test_meta_verbose_names(self):
        self.assertEqual(Question._meta.verbose_name, "pregunta")
        self.assertEqual(Question._meta.verbose_name_plural, "preguntas")

    def test_foreign_key_and_related_name(self):
        q = Question.objects.create(
            examen=self.exam, enunciado="Q1", orden=1, puntaje=10
        )
        self.assertEqual(q.examen, self.exam)
        self.assertEqual(self.exam.preguntas.get(), q)
        related_name = (
            Question._meta.get_field("examen").remote_field.related_name
        )
        self.assertEqual(related_name, "preguntas")


class ChoiceModelTest(TestCase):
    """Tests for the Choice model: fields, str, Meta, FK."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="Choice FK Test", fecha_creacion="2025-02-01"
        )
        self.question = Question.objects.create(
            examen=self.exam, enunciado="Q1", orden=1, puntaje=10
        )

    def test_str_returns_texto(self):
        c = Choice.objects.create(
            pregunta=self.question, texto="Paris", correcta=True, orden=1
        )
        self.assertEqual(str(c), "Paris")

    def test_meta_ordering(self):
        self.assertEqual(Choice._meta.ordering, ["orden"])

    def test_meta_verbose_names(self):
        self.assertEqual(Choice._meta.verbose_name, "opcion")
        self.assertEqual(Choice._meta.verbose_name_plural, "opciones")

    def test_foreign_key_and_related_name(self):
        c = Choice.objects.create(
            pregunta=self.question, texto="Paris", correcta=True, orden=1
        )
        self.assertEqual(c.pregunta, self.question)
        self.assertEqual(self.question.opciones.get(), c)
        related_name = (
            Choice._meta.get_field("pregunta").remote_field.related_name
        )
        self.assertEqual(related_name, "opciones")


# ---------------------------------------------------------------------------
# 2. Migration tests
# ---------------------------------------------------------------------------
class MigrationDefinitionTests(TestCase):
    """Verify migration files contain the expected operations."""

    def test_initial_migration_creates_three_models(self):
        mod = import_module("quiz.migrations.0001_initial")
        ops = [
            op.name
            for op in mod.Migration.operations
            if isinstance(op, migrations.CreateModel)
        ]
        self.assertEqual(ops, ["Exam", "Question", "Choice"])
        self.assertTrue(mod.Migration.initial)

    def test_puntaje_migration_adds_score_field(self):
        mod = import_module("quiz.migrations.0003_question_puntaje")
        operation = mod.Migration.operations[0]
        self.assertIsInstance(operation, migrations.AddField)
        self.assertEqual(operation.model_name, "question")
        self.assertEqual(operation.name, "puntaje")
        self.assertEqual(operation.field.default, 10)

    def test_puntaje_migration_depends_on_alter_fecha(self):
        mod = import_module("quiz.migrations.0003_question_puntaje")
        expected_dep = ("quiz", "0002_alter_exam_fecha_creacion")
        self.assertIn(expected_dep, mod.Migration.dependencies)

    def test_database_has_quiz_tables_and_puntaje_column(self):
        expected_tables = {"quiz_exam", "quiz_question", "quiz_choice"}
        table_names = set(
            connection.introspection.table_names()
        )
        self.assertTrue(expected_tables.issubset(table_names))

        columns = {
            c.name
            for c in connection.introspection.get_table_description(
                connection.cursor(), "quiz_question"
            )
        }
        self.assertIn("id", columns)
        self.assertIn("examen_id", columns)
        self.assertIn("puntaje", columns)


# ---------------------------------------------------------------------------
# 3. Form tests
# ---------------------------------------------------------------------------
class ExamFormTest(TestCase):
    """Tests for ExamForm validation."""

    def test_valid_form(self):
        form = ExamForm(
            data={"titulo": "Valid Exam", "descripcion": "Desc"}
        )
        self.assertTrue(form.is_valid())

    def test_blank_titulo_after_strip(self):
        form = ExamForm(data={"titulo": "   ", "descripcion": "Desc"})
        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)

    def test_empty_titulo_invalid(self):
        form = ExamForm(data={"titulo": "", "descripcion": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)


class QuestionFormTest(TestCase):
    """Tests for QuestionForm."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="Form Test", fecha_creacion="2025-04-01"
        )

    def test_valid_form(self):
        form = QuestionForm(
            data={
                "enunciado": "What is Python?",
                "examen": self.exam.pk,
                "orden": 1,
            }
        )
        self.assertTrue(form.is_valid())


class ChoiceFormTest(TestCase):
    """Tests for ChoiceForm."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="Choice Form Test", fecha_creacion="2025-05-01"
        )
        self.question = Question.objects.create(
            examen=self.exam, enunciado="Q1", orden=1, puntaje=10
        )

    def test_valid_form(self):
        form = ChoiceForm(
            data={"texto": "Paris", "correcta": True}
        )
        self.assertTrue(form.is_valid())

    def test_blank_texto_invalid(self):
        form = ChoiceForm(data={"texto": "   ", "correcta": False})
        self.assertFalse(form.is_valid())
        self.assertIn("texto", form.errors)


# ---------------------------------------------------------------------------
# 4. FormSet tests: exactly-one-correct validation
# ---------------------------------------------------------------------------
class ChoiceFormSetTests(TestCase):
    """Verify the ChoiceFormSet enforces exactly one correct option."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="FormSet Test", fecha_creacion="2025-06-01"
        )
        self.question = Question(
            examen=self.exam, enunciado="FormSet Q", orden=1
        )

    # -- helpers --
    def _build_data(self, correct_indices):
        """Return a POST-dict with 4 choice rows."""
        data = {
            "opciones-TOTAL_FORMS": "4",
            "opciones-INITIAL_FORMS": "0",
            "opciones-MIN_NUM_FORMS": "0",
            "opciones-MAX_NUM_FORMS": "1000",
        }
        for i in range(4):
            data[f"opciones-{i}-texto"] = f"Option {i + 1}"
            if i in correct_indices:
                data[f"opciones-{i}-correcta"] = "on"
        return data

    def test_formset_rejects_zero_correct(self):
        formset = ChoiceFormSet(
            data=self._build_data(set()),
            instance=self.question,
            prefix="opciones",
        )
        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())

    def test_formset_rejects_two_correct(self):
        formset = ChoiceFormSet(
            data=self._build_data({0, 1}),
            instance=self.question,
            prefix="opciones",
        )
        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())

    def test_formset_rejects_three_correct(self):
        formset = ChoiceFormSet(
            data=self._build_data({0, 1, 2}),
            instance=self.question,
            prefix="opciones",
        )
        self.assertFalse(formset.is_valid())

    def test_formset_accepts_exactly_one_correct(self):
        for idx in range(4):
            with self.subTest(correct_idx=idx):
                formset = ChoiceFormSet(
                    data=self._build_data({idx}),
                    instance=self.question,
                    prefix="opciones",
                )
                self.assertTrue(formset.is_valid())

    def test_formset_with_empty_rows_ignored(self):
        """Rows with no texto should be skipped, not cause a 'no correct' error."""
        data = {
            "opciones-TOTAL_FORMS": "3",
            "opciones-INITIAL_FORMS": "0",
            "opciones-MIN_NUM_FORMS": "0",
            "opciones-MAX_NUM_FORMS": "1000",
            "opciones-0-texto": "",
            "opciones-0-correcta": "",
            "opciones-1-texto": "Valid",
            "opciones-1-correcta": "on",
            "opciones-2-texto": "",
            "opciones-2-correcta": "",
        }
        formset = ChoiceFormSet(
            data=data, instance=self.question, prefix="opciones"
        )
        self.assertTrue(formset.is_valid())


# ---------------------------------------------------------------------------
# 5. View tests
# ---------------------------------------------------------------------------
class ExamListViewTest(TestCase):
    """GET /examenes/ returns 200 with correct context and ordering."""

    def setUp(self):
        Exam.objects.create(titulo="Old", fecha_creacion="2025-01-01")
        Exam.objects.create(titulo="New", fecha_creacion="2025-12-31")

    def test_status_and_template(self):
        resp = self.client.get(reverse("quiz:exam_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quiz/exam_list.html")

    def test_context_contains_exam_list(self):
        resp = self.client.get(reverse("quiz:exam_list"))
        self.assertEqual(
            list(resp.context["exam_list"]),
            list(Exam.objects.order_by("-fecha_creacion")),
        )

    def test_list_contains_exam_links(self):
        resp = self.client.get(reverse("quiz:exam_list"))
        for exam in Exam.objects.all():
            self.assertContains(resp, exam.titulo)
            self.assertContains(
                resp,
                reverse("quiz:exam_detail", args=[exam.pk]),
            )

    def test_empty_list_shows_info(self):
        Exam.objects.all().delete()
        resp = self.client.get(reverse("quiz:exam_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No hay exámenes creados")


class ExamDetailViewTest(TestCase):
    """GET /examen/<pk>/ returns questions and choices in context."""

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="Detail Exam", fecha_creacion="2025-07-01"
        )
        self.q1 = Question.objects.create(
            examen=self.exam, enunciado="Q1 text", orden=1, puntaje=10
        )
        Choice.objects.create(
            pregunta=self.q1, texto="Correct", correcta=True, orden=1
        )
        Choice.objects.create(
            pregunta=self.q1, texto="Wrong", correcta=False, orden=2
        )

    def test_status_and_template(self):
        resp = self.client.get(
            reverse("quiz:exam_detail", args=[self.exam.pk])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quiz/exam_detail.html")

    def test_context(self):
        resp = self.client.get(
            reverse("quiz:exam_detail", args=[self.exam.pk])
        )
        self.assertEqual(resp.context["exam"], self.exam)
        self.assertEqual(resp.context["preguntas"].count(), 1)

    def test_content_contains_questions_and_choices(self):
        resp = self.client.get(
            reverse("quiz:exam_detail", args=[self.exam.pk])
        )
        self.assertContains(resp, "Q1 text")
        self.assertContains(resp, "Correct")
        self.assertContains(resp, "Wrong")

    def test_exam_with_no_questions(self):
        """Edge case: an exam that has zero questions."""
        empty_exam = Exam.objects.create(
            titulo="Empty", fecha_creacion="2025-08-01"
        )
        resp = self.client.get(
            reverse("quiz:exam_detail", args=[empty_exam.pk])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No hay preguntas para este examen")


class ExamCreateViewTest(TestCase):
    """POST /examen/nuevo/ creates an Exam and redirects."""

    def test_get_shows_form(self):
        resp = self.client.get(reverse("quiz:exam_create"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quiz/exam_create.html")

    def test_post_creates_exam(self):
        resp = self.client.post(
            reverse("quiz:exam_create"),
            {"titulo": "Created Exam", "descripcion": "Via POST"},
        )
        self.assertRedirects(resp, reverse("quiz:exam_list"))
        self.assertEqual(Exam.objects.count(), 1)
        self.assertEqual(Exam.objects.first().titulo, "Created Exam")


class QuestionCreateViewTest(TestCase):
    """
    POST /examen/<id>/pregunta/nueva/ — validates form + formset,
    enforces exactly one correct choice, persists data, redirects.
    """

    def setUp(self):
        self.exam = Exam.objects.create(
            titulo="Question View Test", fecha_creacion="2025-09-01"
        )
        _create_admin_user()

    def _url(self):
        return reverse(
            "quiz:question_create", kwargs={"exam_id": self.exam.pk}
        )

    def _post_data(self, correct_indices):
        data = {
            "enunciado": "View question?",
            "examen": self.exam.pk,
            "orden": 1,
            "opciones-TOTAL_FORMS": "4",
            "opciones-INITIAL_FORMS": "0",
            "opciones-MIN_NUM_FORMS": "0",
            "opciones-MAX_NUM_FORMS": "1000",
        }
        for i in range(4):
            data[f"opciones-{i}-texto"] = f"View option {i + 1}"
            if i in correct_indices:
                data[f"opciones-{i}-correcta"] = "on"
        return data

    def test_get_shows_form_and_context(self):
        self.client.login(username="test-admin", password="admin123")
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quiz/question_create.html")
        self.assertIn("form", resp.context)
        self.assertIn("formset", resp.context)
        self.assertIn("exam", resp.context)
        self.assertEqual(resp.context["exam"], self.exam)

    def test_post_exactly_one_correct_saves_and_redirects(self):
        self.client.login(username="test-admin", password="admin123")
        resp = self.client.post(self._url(), self._post_data({2}))
        self.assertRedirects(
            resp, reverse("quiz:exam_detail", args=[self.exam.pk])
        )
        self.assertEqual(Question.objects.count(), 1)
        q = Question.objects.first()
        self.assertEqual(q.enunciado, "View question?")
        self.assertEqual(Choice.objects.filter(pregunta=q).count(), 4)
        self.assertEqual(
            Choice.objects.filter(pregunta=q, correcta=True).count(), 1
        )

    def test_post_zero_correct_returns_errors(self):
        self.client.login(username="test-admin", password="admin123")
        resp = self.client.post(self._url(), self._post_data(set()))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quiz/question_create.html")
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Choice.objects.count(), 0)

    def test_post_two_correct_returns_errors(self):
        self.client.login(username="test-admin", password="admin123")
        resp = self.client.post(self._url(), self._post_data({0, 1}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_post_blank_enunciado_fails(self):
        self.client.login(username="test-admin", password="admin123")
        data = self._post_data({0})
        data["enunciado"] = ""
        resp = self.client.post(self._url(), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_question_created_has_puntaje(self):
        self.client.login(username="test-admin", password="admin123")
        resp = self.client.post(self._url(), self._post_data({1}))
        self.assertRedirects(
            resp, reverse("quiz:exam_detail", args=[self.exam.pk])
        )
        q = Question.objects.first()
        self.assertEqual(q.puntaje, 10)


# ---------------------------------------------------------------------------
# 6. Admin tests
# ---------------------------------------------------------------------------
class QuizAdminTests(TestCase):
    """Verify admin registration and the exam-creation flow."""

    def setUp(self):
        self.admin_user = _create_admin_user()
        self.client.force_login(self.admin_user)

    def test_all_models_registered(self):
        self.assertTrue(admin.site.is_registered(Exam))
        self.assertTrue(admin.site.is_registered(Question))
        self.assertTrue(admin.site.is_registered(Choice))

    def test_exam_list_page_loads(self):
        """The admin changelist for each model loads with 200."""
        for model in (Exam, Question, Choice):
            url = reverse(
                f"admin:quiz_{model._meta.model_name}_changelist"
            )
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

    @override_settings(
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
        CSRF_TRUSTED_ORIGINS=["https://testserver", "http://testserver"],
    )
    def test_admin_flow_create_exam_two_questions_four_choices_each(self):
        """
        End-to-end admin flow:
          1. Create an Exam
          2. Create 2 Questions linked to it
          3. For each question, create 4 Choices with exactly 1 correct
        """
        # Obtain CSRF token by GETting the add page
        exam_get = self.client.get(reverse("admin:quiz_exam_add"))
        self.assertEqual(exam_get.status_code, 200)
        csrf_token = self.client.cookies.get("csrftoken")

        # Step 1: create exam
        exam_resp = self.client.post(
            reverse("admin:quiz_exam_add"),
            {
                "titulo": "Admin Evidence Exam",
                "descripcion": "Created through admin UI",
                "fecha_creacion": "2025-01-01",
                "_save": "Save",
            },
            **({"HTTP_X_CSRFTOKEN": csrf_token.value} if csrf_token else {}),
        )
        if exam_resp.status_code != 302:
            content = exam_resp.content.decode()
            import re
            error_msgs = re.findall(
                r'<li[^>]*>(.*?)</li>', content, re.DOTALL
            )
            self.fail(
                "Admin exam creation failed (status %d). Errors: %s"
                % (exam_resp.status_code, error_msgs)
            )
        exam = Exam.objects.get(titulo="Admin Evidence Exam")

        # Step 2: create two questions
        for number in range(2):
            q_get = self.client.get(reverse("admin:quiz_question_add"))
            self.assertEqual(q_get.status_code, 200)
            q_csrf = self.client.cookies.get("csrftoken")
            q_resp = self.client.post(
                reverse("admin:quiz_question_add"),
                {
                    "examen": exam.pk,
                    "enunciado": f"Admin question {number + 1}",
                    "orden": number + 1,
                    "puntaje": "10",
                    "_save": "Save",
                },
                **({"HTTP_X_CSRFTOKEN": q_csrf.value} if q_csrf else {}),
            )
            if q_resp.status_code != 302:
                content = q_resp.content.decode()
                # Look for form error <li> elements
                import re
                error_msgs = re.findall(
                    r'<li[^>]*>(.*?)</li>', content, re.DOTALL
                )
                self.fail(
                    "Question POST failed (status %d). Errors: %s"
                    % (q_resp.status_code, error_msgs)
                )

        self.assertEqual(exam.preguntas.count(), 2)

        # Step 3: create four choices per question
        for question in exam.preguntas.all():
            for opt in range(4):
                c_get = self.client.get(reverse("admin:quiz_choice_add"))
                self.assertEqual(c_get.status_code, 200)
                c_csrf = self.client.cookies.get("csrftoken")
                c_resp = self.client.post(
                    reverse("admin:quiz_choice_add"),
                    {
                        "pregunta": question.pk,
                        "texto": f"Option {opt + 1} for Q{question.pk}",
                        "correcta": "on" if opt == 0 else "",
                        "orden": opt + 1,
                        "_save": "Save",
                    },
                    **({"HTTP_X_CSRFTOKEN": c_csrf.value} if c_csrf else {}),
                )
                if c_resp.status_code != 302:
                    content = c_resp.content.decode()
                    import re
                    error_msgs = re.findall(
                        r'<li[^>]*>(.*?)</li>', content, re.DOTALL
                    )
                    self.fail(
                        "Choice POST failed (status %d). Errors: %s"
                        % (c_resp.status_code, error_msgs)
                    )

        # Verify
        for question in exam.preguntas.all():
            self.assertEqual(question.opciones.count(), 4)
            self.assertEqual(
                question.opciones.filter(correcta=True).count(), 1
            )


# ---------------------------------------------------------------------------
# 7. Edge cases
# ---------------------------------------------------------------------------
class EdgeCaseTests(TestCase):
    """Edge cases: exam with no questions; question with no valid options."""

    def test_exam_with_no_questions_listed(self):
        Exam.objects.create(titulo="Empty Exam", fecha_creacion="2025-01-01")
        resp = self.client.get(reverse("quiz:exam_list"))
        self.assertEqual(resp.status_code, 200)
        titles = [e.titulo for e in resp.context["exam_list"]]
        self.assertIn("Empty Exam", titles)

    def test_question_with_no_valid_options_rejected(self):
        self.exam = Exam.objects.create(
            titulo="Edge Exam", fecha_creacion="2025-02-01"
        )
        _create_admin_user()
        self.client.login(username="test-admin", password="admin123")

        data = {
            "enunciado": "Edge question",
            "examen": self.exam.pk,
            "orden": 1,
            "opciones-TOTAL_FORMS": "2",
            "opciones-INITIAL_FORMS": "0",
            "opciones-MIN_NUM_FORMS": "0",
            "opciones-MAX_NUM_FORMS": "1000",
            "opciones-0-texto": "",
            "opciones-0-correcta": "",
            "opciones-1-texto": "",
            "opciones-1-correcta": "",
        }
        url = reverse("quiz:question_create", kwargs={"exam_id": self.exam.pk})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_exam_detail_with_multiple_questions(self):
        exam = Exam.objects.create(
            titulo="Multi Q Exam", fecha_creacion="2025-03-01"
        )
        for i in range(3):
            q = Question.objects.create(
                examen=exam, enunciado=f"Q{i}", orden=i, puntaje=10
            )
            Choice.objects.create(
                pregunta=q, texto="A", correcta=True, orden=1
            )
            Choice.objects.create(
                pregunta=q, texto="B", correcta=False, orden=2
            )

        resp = self.client.get(
            reverse("quiz:exam_detail", args=[exam.pk])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["preguntas"].count(), 3)
        self.assertContains(resp, "Q0")
        self.assertContains(resp, "Q1")
        self.assertContains(resp, "Q2")

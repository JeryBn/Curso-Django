from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from quiz.forms import ChoiceFormSet, ExamForm, QuestionForm
from quiz.models import Exam, Question


# ---------------------------------------------------------------------------
# 1. exam_list – ListView: listar todos los examenes ordenados por fecha
# ---------------------------------------------------------------------------
class ExamListView(ListView):
    """Muestra todos los exámenes ordenados por fecha_creacion descendente."""

    model = Exam
    template_name = 'quiz/exam_list.html'
    context_object_name = 'exam_list'

    def get_queryset(self):
        return super().get_queryset().order_by('-fecha_creacion')


# ---------------------------------------------------------------------------
# 2. exam_detail – DetailView: detalle de un examen con preguntas y opciones
# ---------------------------------------------------------------------------
class ExamDetailView(DetailView):
    """Muestra un examen con sus preguntas y cada pregunta con sus opciones."""

    model = Exam
    template_name = 'quiz/exam_detail.html'
    context_object_name = 'exam'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'preguntas'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        context['preguntas'] = exam.preguntas.all()
        return context


# ---------------------------------------------------------------------------
# 3. question_create – CreateView: dar de alta una pregunta con sus opciones
# ---------------------------------------------------------------------------
class QuestionCreateView(CreateView):
    """
    Crea una pregunta nueva dentro de un examen.
    Recibe el pk del examen por la URL (kwargs['exam_id']).
    Usa QuestionForm + ChoiceFormSet y valida que EXACTAMENTE una opción
    tenga correcta=True.
    """

    model = Question
    form_class = QuestionForm
    template_name = 'quiz/question_create.html'
    context_object_name = 'question_form'

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _get_exam(self):
        """Obtiene el examen desde kwargs o retorna 404."""
        return get_object_or_404(Exam, pk=self.kwargs['exam_id'])

    def _build_formset(self, data=None, files=None, **kwargs):
        """Retorna una instancia del formset (vacía o con data)."""
        return ChoiceFormSet(
            data=data,
            files=files,
            instance=kwargs.pop('instance', None),
            **kwargs,
        )

    # ------------------------------------------------------------------
    # GET – muestra los formularios
    # ------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        # Fijar el examen (hidden / disabled)
        exam = self._get_exam()
        if not form.initial.get('examen'):
            form.initial['examen'] = exam.pk

        formset = self._build_formset(instance=form.instance if form.instance else None)
        context['formset'] = formset
        context['exam'] = exam
        return context

    def get(self, request, *args, **kwargs):
        self.object = None  # necesario para que super().get_context_data() funcione
        return super().get(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # POST – valida y guarda
    # ------------------------------------------------------------------
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        exam = self._get_exam()

        # Forzar el examen en el form
        form.fields['examen'].initial = exam.pk
        form.initial['examen'] = exam.pk

        formset = self._build_formset(data=request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            # --- Validación crítica: exactamente UNA correcta ---
            correctas = sum(1 for cf in formset.cleaned_data if cf.get('correcta'))
            if correctas != 1:
                form.add_error(
                    None,
                    'Debe marcar exactamente una opción como correcta. '
                    'Encontradas: {}.'.format(correctas),
                )
                # Re-renderizamos con los errores.
                return self.render_to_response(
                    self.get_context_data(form=form, formset=formset, exam=exam),
                )

            return self.form_valid(form, formset, exam)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset, exam=exam),
            )

    def form_valid(self, form, formset, exam):
        """Guarda pregunta y opciones, luego redirige al detalle del examen."""
        form.instance.exam = exam
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return redirect('quiz:exam_detail', pk=exam.pk)

    # ------------------------------------------------------------------
    # form_invalid: re-render con los datos para corregir
    # ------------------------------------------------------------------
    def form_invalid(self, form):
        formset = self._build_formset(data=self.request.POST)
        exam = self._get_exam()
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset, exam=exam),
        )


# ---------------------------------------------------------------------------
# 4. exam_create – CreateView: dar de alta un nuevo examen
# ---------------------------------------------------------------------------
class ExamCreateView(CreateView):
    """Crea un nuevo examen."""

    model = Exam
    form_class = ExamForm
    template_name = 'quiz/exam_create.html'
    success_url = reverse_lazy('quiz:exam_list')


@login_required
def login_required_question_create(request, *args, **kwargs):
    """
    Wrapper funcional que fuerza login_required sobre QuestionCreateView.
    """
    view = QuestionCreateView()
    view.setup(request, *args, **kwargs)
    return view.dispatch(request, *args, **kwargs)

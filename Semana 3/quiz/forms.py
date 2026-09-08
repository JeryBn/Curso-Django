from django import forms
from .models import Exam, Question, Choice


# ---------------------------------------------------------------------------
# 1. ExamForm – ModelForm para el modelo Exam
# ---------------------------------------------------------------------------
class ExamForm(forms.ModelForm):
    """Formulario para crear y editar un examen."""

    class Meta:
        model = Exam
        fields = ['titulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del examen',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del examen (opcional)',
            }),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            titulo = titulo.strip()
            if not titulo:
                raise forms.ValidationError('El título no puede estar vacío.')
        return titulo


# ---------------------------------------------------------------------------
# 2. QuestionForm – ModelForm para el modelo Question
# ---------------------------------------------------------------------------
class QuestionForm(forms.ModelForm):
    """Formulario para crear y editar una pregunta."""

    class Meta:
        model = Question
        fields = ['enunciado', 'examen', 'orden']
        widgets = {
            'enunciado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enunciado de la pregunta',
            }),
            'examen': forms.Select(attrs={
                'class': 'form-control',
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
        }


# ---------------------------------------------------------------------------
# 3. ChoiceForm – ModelForm para el modelo Choice
# ---------------------------------------------------------------------------
class ChoiceForm(forms.ModelForm):
    """Formulario individual para una opción ( Choice )."""

    class Meta:
        model = Choice
        fields = ['texto', 'correcta']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto de la opción',
            }),
            'correcta': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        texto = cleaned_data.get('texto')
        if texto:
            texto = texto.strip()
            if not texto:
                raise forms.ValidationError('El texto de la opción no puede estar vacío.')
            cleaned_data['texto'] = texto
        return cleaned_data


# ---------------------------------------------------------------------------
# 4. ChoiceFormSet – formset de Choice vinculado a Question
# ---------------------------------------------------------------------------
class ChoiceFormSetForm(ChoiceForm):
    """
    Subclase de ChoiceForm que tolera filas vacías (las ignora como
    entradas no usadas del formset extra=1).
    """

    def clean_texto(self):
        texto = self.cleaned_data.get('texto')
        if not texto:
            # Fila vacía generada por extra=1: se ignora (se tratará
            # como "no usada" durante el save del formset).
            return ''
        texto = texto.strip()
        if not texto:
            raise forms.ValidationError('El texto de la opción no puede estar vacío.')
        return texto

    def clean(self):
        cleaned_data = super().clean()
        # Si la fila fue marcada para eliminar, ignórala.
        if self.cleaned_data.get('DELETE', False):
            return cleaned_data
        return cleaned_data


class ChoiceFormSetFormSet(forms.BaseInlineFormSet):
    """
    Enforces that exactly one valid (non-empty) choice is marked correct.
    Empty rows (blank texto) are ignored.
    """

    def clean(self):
        super().clean()
        correct_count = 0
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE') or form.cleaned_data.get('texto') == '':
                continue
            if form.cleaned_data.get('correcta'):
                correct_count += 1
        if correct_count != 1:
            raise forms.ValidationError(
                'Debe marcar exactamente una opción como correcta. '
                'Encontradas: {}.'.format(correct_count)
            )


ChoiceFormSet = forms.inlineformset_factory(
    parent_model=Question,
    model=Choice,
    form=ChoiceFormSetForm,
    formset=ChoiceFormSetFormSet,
    fields=['texto', 'correcta'],
    extra=1,
    can_delete=True,
    can_order=False,
    widgets={
        'texto': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Texto de la opción',
        }),
        'correcta': forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
    },
)

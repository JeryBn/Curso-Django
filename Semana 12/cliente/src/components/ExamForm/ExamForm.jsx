import React, { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createExam, requestError } from '../../api/exams';

export default function ExamForm() {
  const [title, setTitle] = useState('');
  const [titleError, setTitleError] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const titleInput = useRef(null);
  const navigate = useNavigate();

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setTitleError('');
    setError('');
    try {
      await createExam(title);
      navigate('/examenes');
    } catch (failure) {
      const messages = failure.response?.data?.title;
      if (Array.isArray(messages)) {
        setTitleError(messages.join(' '));
        titleInput.current?.focus();
      } else {
        setError(requestError(failure));
      }
    } finally {
      setSaving(false);
    }
  }

  return <section aria-labelledby="new-exam-title">
    <Link to="/examenes">Volver al listado</Link>
    <h1 id="new-exam-title">Nuevo examen</h1>
    <form className="exam-form" onSubmit={submit} noValidate>
      <label htmlFor="exam-title">Título del examen (obligatorio)</label>
      <input id="exam-title" ref={titleInput} value={title} onChange={event => setTitle(event.target.value)}
        required aria-invalid={Boolean(titleError)} aria-describedby={titleError ? 'title-error' : undefined} />
      {titleError && <p className="exam-error" id="title-error" role="alert">{titleError}</p>}
      {error && <p className="exam-error" role="alert">{error}</p>}
      <button className="exam-primary" disabled={saving}>{saving ? 'Guardando…' : 'Guardar examen'}</button>
    </form>
  </section>;
}

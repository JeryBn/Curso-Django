import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { deleteExam, listExams, requestError } from '../../api/exams';

export default function ExamList({ token }) {
  const [page, setPage] = useState(1);
  const [revision, setRevision] = useState(0);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError('');
    listExams(page, controller.signal)
      .then(result => {
        if (!controller.signal.aborted) setData(result);
      })
      .catch(failure => {
        if (controller.signal.aborted) return;
        if (failure.response?.status === 404 && page > 1) {
          setPage(page - 1);
          return;
        }
        setError(requestError(failure));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [page, revision, token]);

  async function remove(exam) {
    setDeleting(true);
    setDeleteError('');
    try {
      await deleteExam(exam.id);
      setRevision(current => current + 1);
    } catch (failure) {
      setDeleteError(requestError(failure));
    } finally {
      setDeleting(false);
    }
  }

  return <section aria-labelledby="exams-title">
    <div className="exam-toolbar">
      <div><h1 id="exams-title">Exámenes</h1><p>Gestiona los cuestionarios de la API de Django.</p></div>
      <Link className="exam-primary" to="/examenes/nuevo">Nuevo examen</Link>
    </div>
    {loading ? <div className="exam-skeleton" role="status" aria-busy="true">
      <p>Cargando exámenes…</p><div /><div /><div />
    </div> : error ? <div className="exam-error" role="alert">
      <p>{error}</p>
      <button onClick={() => setRevision(current => current + 1)}>Reintentar</button>
    </div> : data && <>
      {deleteError && <p className="exam-error" role="alert">{deleteError}</p>}
      <p role="status">{data.count} exámenes registrados</p>
      {data.results.length ? <div className="exam-table-wrap"><table>
        <thead><tr><th scope="col">ID</th><th scope="col">Título</th><th scope="col">Preguntas</th><th scope="col">Acciones</th></tr></thead>
        <tbody>{data.results.map(exam => <tr key={exam.id}>
          <td>{exam.id}</td><td>{exam.title}</td><td>{exam.question_count}</td>
          <td><button className="exam-delete" type="button" disabled={deleting} onClick={() => remove(exam)} aria-label={`Eliminar ${exam.title}`}>Eliminar</button></td>
        </tr>)}</tbody>
      </table></div> : <p>Todavía no hay exámenes. Crea el primero desde el formulario.</p>}
      {(data.previous || data.next) && <nav className="exam-pagination" aria-label="Paginación">
        <button disabled={!data.previous || deleting} onClick={() => setPage(page - 1)}>Anterior</button>
        <span>Página {page}</span>
        <button disabled={!data.next || deleting} onClick={() => setPage(page + 1)}>Siguiente</button>
      </nav>}
      </>}
  </section>;
}

import React, { useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { setToken } from '../../api/exams';
import ExamList from '../ExamList/ExamList';
import ExamForm from '../ExamForm/ExamForm';
import './exam.css';

const tokenKey = 'lab12:exam-token';
setToken(sessionStorage.getItem(tokenKey));

export default function ExamWorkspace() {
  const [token, updateToken] = useState(() => sessionStorage.getItem(tokenKey) || '');
  const [draft, setDraft] = useState('');

  function saveToken(event) {
    event.preventDefault();
    const value = draft.trim();
    if (value) sessionStorage.setItem(tokenKey, value);
    else sessionStorage.removeItem(tokenKey);
    setToken(value);
    updateToken(value);
    setDraft('');
  }

  return <main className="exam-workspace">
    <details className="exam-access" open={token ? undefined : true}>
      <summary>{token ? 'Acceso configurado' : 'Configurar acceso a Django'}</summary>
      <form onSubmit={saveToken}>
        <label htmlFor="exam-token">Token local del usuario profe</label>
        <input id="exam-token" type="password" autoComplete="off" value={draft} onChange={event => setDraft(event.target.value)} />
        <button>Guardar acceso</button>
        {token && <button type="button" onClick={() => {
          sessionStorage.removeItem(tokenKey);
          setToken('');
          updateToken('');
          setDraft('');
        }}>Cerrar acceso</button>}
      </form>
    </details>
    <Routes>
      <Route index element={<ExamList token={token} />} />
      <Route path="nuevo" element={<ExamForm />} />
    </Routes>
  </main>;
}

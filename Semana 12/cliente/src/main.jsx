import React from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, Link, Route, Routes } from 'react-router-dom';
import App from './App.jsx';
import ExamWorkspace from './components/ExamWorkspace/ExamWorkspace.jsx';
import './styles/base.css';

createRoot(document.getElementById('root')).render(
  <HashRouter>
    <nav className="exam-nav" aria-label="Secciones">
      <Link to="/">Cartelera</Link>
      <Link to="/examenes">Exámenes</Link>
    </nav>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/examenes/*" element={<ExamWorkspace />} />
    </Routes>
  </HashRouter>,
);



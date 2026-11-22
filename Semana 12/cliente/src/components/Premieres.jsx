import React, { useState } from 'react';
import { usePremieres } from '../hooks/usePremieres.js';
import { useWindowSize } from '../hooks/useWindowSize.js';
import Button from './Button.jsx';

function Skeleton() {
  return <div className="skeleton" role="status">Cargando estrenos…</div>;
}

function Carousel({ movies }) {
  const [index, setIndex] = useState(0);
  const width = useWindowSize();
  const movie = movies[index];
  return <div className={width < 600 ? 'premiere compact' : 'premiere'}>
    <img src={movie.image} alt={movie.title} /><div><h3>{movie.title}</h3><p>{movie.synopsis}</p>
    <Button variant="secondary" aria-label="Estreno anterior" onClick={() => setIndex(i => (i + movies.length - 1) % movies.length)}>Anterior</Button>
    <Button aria-label="Siguiente estreno" onClick={() => setIndex(i => (i + 1) % movies.length)}>Siguiente</Button></div>
  </div>;
}

export default function Premieres({ movies }) {
  const [request, setRequest] = useState({ fail: false, attempt: 0 });
  const result = usePremieres(movies, request.fail, request.attempt);
  function reload(fail) { setRequest(previous => ({ fail, attempt: previous.attempt + 1 })); }
  return <section><h2>Estrenos</h2>
    {result.status === 'loading' && <Skeleton />}
    {result.status === 'error' && <div role="alert"><p>No se pudieron cargar los estrenos. Intenta nuevamente.</p><Button onClick={() => reload(false)}>Reintentar</Button></div>}
    {result.status === 'ready' && <Carousel movies={result.data} />}
    <Button variant="secondary" onClick={() => reload(true)}>Simular error</Button>
  </section>;
}

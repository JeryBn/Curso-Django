import React from 'react';
import { useWindowSize } from '../hooks/useWindowSize.js';
import MovieCard from './MovieCard.jsx';

export default function MovieList({ movies, filter, favorites, onToggle }) {
  const width = useWindowSize();
  const columns = width < 540 ? 1 : width < 830 ? 2 : width < 1120 ? 3 : 4;
  const visible = movies.filter(movie => movie.title.toLocaleLowerCase('es').includes(filter.trim().toLocaleLowerCase('es')));
  return <section id="cartelera"><h2>Cartelera</h2>
    {visible.length ? <div className="grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>{visible.map(movie => <MovieCard key={movie.id} movie={movie} favorite={favorites.includes(movie.id)} onToggle={onToggle} />)}</div>
      : <p role="status">No hay películas que coincidan con la búsqueda.</p>}
  </section>;
}


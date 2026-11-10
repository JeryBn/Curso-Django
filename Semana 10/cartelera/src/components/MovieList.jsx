import React from 'react';
import MovieCard from './MovieCard.jsx';

export default function MovieList({ movies, filter, favorites, onToggle }) {
  const visible = movies.filter(movie => movie.title.toLocaleLowerCase('es').includes(filter.trim().toLocaleLowerCase('es')));
  return <section id="cartelera"><h2>Cartelera</h2>
    {visible.length ? <div className="grid">{visible.map(movie => <MovieCard key={movie.id} movie={movie} favorite={favorites.includes(movie.id)} onToggle={onToggle} />)}</div>
      : <p role="status">No hay películas que coincidan con la búsqueda.</p>}
  </section>;
}


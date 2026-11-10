import React from 'react';
import Button from './Button.jsx';

export default function MovieCard({ movie, favorite, onToggle }) {
  return <article><img src={movie.image} alt={movie.title} /><div className="details">
    <h3>{movie.title}</h3><p>{movie.rating}/10 · {movie.classification}</p><p>{movie.synopsis}</p><p>{movie.showtimes.join(' · ')}</p>
    <Button variant={favorite ? 'primary' : 'secondary'} aria-pressed={favorite} onClick={() => onToggle(movie.id)}>{favorite ? 'Quitar favorita' : 'Marcar favorita'}</Button>
  </div></article>;
}


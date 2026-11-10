import React from 'react';
import MovieCard from './MovieCard.jsx';

export default function MovieList({ movies }) {
  return <section id="cartelera"><h2>Cartelera</h2><div className="grid">{movies.map(movie => <MovieCard key={movie.id} movie={movie} />)}</div></section>;
}

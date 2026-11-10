import React, { useEffect, useState } from 'react';
import { Header, Footer, Hero } from './components/Layout.jsx';
import MovieList from './components/MovieList.jsx';
import MovieSearch from './components/MovieSearch.jsx';
import { movies } from './data/movies.js';

function loadFavorites() {
  try {
    const stored = JSON.parse(localStorage.getItem('cine:favoritas') ?? '[]');
    return Array.isArray(stored) ? stored.filter(Number.isInteger) : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [favorites, setFavorites] = useState(loadFavorites);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    localStorage.setItem('cine:favoritas', JSON.stringify(favorites));
  }, [favorites]);

  useEffect(() => {
    const timer = setTimeout(() => {
      console.debug('Filtro aplicado:', query);
      setFilter(query);
    }, 350);
    return () => clearTimeout(timer);
  }, [query]);

  function toggleFavorite(id) {
    setFavorites(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]);
  }

  return <><Header /><main>
    <Hero movie={movies[0]}><MovieSearch value={query} onChange={setQuery} /></Hero>
    <MovieList movies={movies} filter={filter} favorites={favorites} onToggle={toggleFavorite} />
  </main><Footer /></>;
}


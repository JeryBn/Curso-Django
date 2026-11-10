import React, { useEffect, useState } from 'react';
import { Header, Footer, Hero } from './components/Layout.jsx';
import MovieList from './components/MovieList.jsx';
import MovieSearch from './components/MovieSearch.jsx';
import { movies as catalog } from './data/movies.js';
import { adaptMovie } from './data/adapter.js';
import { useDebounce } from './hooks/useDebounce.js';
import Premieres from './components/Premieres.jsx';
import Button from './components/Button.jsx';
import toast, { Toaster } from 'react-hot-toast';

const movies = catalog.map(adaptMovie);

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
  const filter = useDebounce(query);

  useEffect(() => {
    localStorage.setItem('cine:favoritas', JSON.stringify(favorites));
  }, [favorites]);

  function toggleFavorite(id) {
    toast(favorites.includes(id) ? 'Favorita eliminada' : 'Favorita guardada');
    setFavorites(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]);
  }

  return <><Toaster /><Header count={favorites.length} /><main>
    <Hero movie={movies[0]}><MovieSearch value={query} onChange={setQuery} /><Button variant="secondary" onClick={() => setQuery('')}>Limpiar filtro</Button></Hero>
    <Premieres movies={movies} />
    <MovieList movies={movies} filter={filter} favorites={favorites} onToggle={toggleFavorite} />
  </main><Footer /></>;
}


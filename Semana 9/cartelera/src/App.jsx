import React from 'react';
import { Header, Footer, Hero } from './components/Layout.jsx';
import MovieList from './components/MovieList.jsx';
import { movies } from './data/movies.js';

export default function App() {
  return <><Header /><main><Hero movie={movies[0]} /><MovieList movies={movies} /></main><Footer /></>;
}

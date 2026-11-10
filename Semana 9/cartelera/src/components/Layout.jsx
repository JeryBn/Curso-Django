import React from 'react';

export function Header() {
  return <header><strong>Cine Horizonte</strong><nav><a href="#cartelera">Cartelera</a> · <a href="#contacto">Contacto</a></nav></header>;
}

export function Hero({ movie }) {
  return <section className="hero"><span>PELÍCULA DESTACADA</span><h1>{movie.title}</h1><p>{movie.synopsis}</p><a href="#cartelera">Ver horarios</a></section>;
}

export function Footer() {
  return <footer id="contacto">Cine Horizonte · Lima · contacto@cinehorizonte.example</footer>;
}

import React from 'react';

export default function MovieSearch({ value, onChange }) {
  return <label className="search">Buscar por título
    <input type="search" value={value} onChange={event => onChange(event.target.value)} placeholder="Ej. Órbita" />
  </label>;
}


# GLAB S10 · Cine Horizonte

Estudiante: Jery Becerra Ninaquispe.

Desde esta carpeta, ejecutar `npm ci` y `npm run dev`. Para compilar, ejecutar `npm run build`.

Button recibe children y variant. MovieSearch es controlado por App; el texto inmediato se separa del filtro que se aplica tras 350 ms. MovieList deriva coincidencias y muestra el estado vacío. MovieCard emite onToggle con el id; App actualiza favoritas y las persiste en localStorage.

Pruebas observadas: búsqueda sin coincidencias y una favorita conservada al recargar. Evidencias en evidencias/.

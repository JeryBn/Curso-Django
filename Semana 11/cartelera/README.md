# GLAB S11 · Cine Horizonte

Estudiante: Jery Becerra Ninaquispe.

Desde esta carpeta, ejecutar `npm ci` y `npm run dev`. Para compilar, ejecutar `npm run build`.

App conserva la consulta y los ids favoritos. Hero alberga el buscador y el botón de limpieza, MovieList recibe el filtro y Header recibe solo el total derivado. El contador se calcula donde vive la lista; Header no puede mantenerlo por separado sin duplicar el estado.

adaptMovie normaliza el catálogo. useDebounce se ocupa de la espera. useWindowSize se comparte entre MovieList y el carrusel. Premieres mantiene la intención de recarga y usa usePremieres para los estados de carga, datos y error. Carousel posee el índice; App muestra las notificaciones mediante react-hot-toast.

Pruebas observadas: carga, fallo simulado, reintento, navegación del carrusel y contador de favoritas. Evidencias en evidencias/.

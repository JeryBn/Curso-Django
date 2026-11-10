# GLAB S09 · Cine Horizonte

Estudiante: Jery Becerra Ninaquispe.

Desde esta carpeta, ejecutar `npm ci` y `npm run dev`. Para compilar, ejecutar `npm run build`.

Ocho películas ficticias con carteles SVG locales. App compone Header, Hero, MovieList y Footer. Hero recibe la destacada; MovieList usa map con id estable y cada MovieCard recibe su película.

Prueba observada: ocho tarjetas visibles. Evidencia: evidencias/cartelera.jpg.

## Reproducción de errores solicitados

Con Vite activo abre errores.html?tipo=class, errores.html?tipo=key y errores.html?tipo=raiz, respectivamente. Las pruebas viven fuera de la entrada principal.

| Cambio | Mensaje observado | Corrección |
|---|---|---|
| class | Invalid DOM property. Did you mean className? | Usar className |
| map sin clave | Each child in a list should have a unique key prop | Usar el id estable |
| Dos nodos raíz consecutivos | Transform failed: Unterminated regular expression (Vite/esbuild) | Envolver con un fragmento JSX |

La captura evidencias/error-raices-jsx.jpg corresponde al tercer caso.
